"""
Regulation Embedder.

Chunks regulation full_text into semantic segments, embeds them using the
existing EmbeddingService, and persists them in a dedicated FAISS index
(separate from the document ingestion index) with a JSON metadata sidecar.

Each chunk is tagged with: regulation_id, jurisdiction, regulation_name,
chunk_index, and the raw text so retrieval can reconstruct citations.
"""

import json
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    faiss = None
    FAISS_AVAILABLE = False
import numpy as np
from pathlib import Path
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

from app.config import get_settings
from app.services.embedder import get_embedding_service
from app.store.models import Regulation

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Target ~600 characters per chunk with 100-char overlap.
# 600 chars ≈ 120–150 tokens for typical English legal text (4-5 chars/token).
CHUNK_SIZE = 2400       # chars  → ~500–600 tokens
CHUNK_OVERLAP = 300     # chars  → ~60–80 tokens overlap between chunks

REGULATION_INDEX_FILENAME = "regulation_index.faiss"
REGULATION_META_FILENAME = "regulation_meta.json"


# ---------------------------------------------------------------------------
# Chunking helpers
# ---------------------------------------------------------------------------

def _split_into_chunks(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split regulation full_text into overlapping character-based chunks,
    respecting paragraph and sentence boundaries where possible.
    """
    if not text or not text.strip():
        return []

    # Prefer splitting on double-newlines (paragraphs)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [text.strip()]

    chunks: List[str] = []
    current = ""

    for paragraph in paragraphs:
        # If paragraph fits in current chunk, append it
        if len(current) + len(paragraph) + 2 <= chunk_size:
            current = (current + "\n\n" + paragraph).strip()
        else:
            # Finalize current chunk (non-empty)
            if current:
                chunks.append(current)
            # If the paragraph itself exceeds chunk_size, split it further
            if len(paragraph) > chunk_size:
                sub_chunks = _split_large_block(paragraph, chunk_size, overlap)
                if sub_chunks:
                    # Start overlap from end of last sub-chunk
                    chunks.extend(sub_chunks[:-1])
                    current = sub_chunks[-1]
                else:
                    current = ""
            else:
                # Start new chunk with overlap from previous
                overlap_text = _get_tail(current, overlap) if current else ""
                current = (overlap_text + "\n\n" + paragraph).strip() if overlap_text else paragraph
    if current:
        chunks.append(current)

    return [c.strip() for c in chunks if c.strip()]


def _split_large_block(text: str, chunk_size: int, overlap: int) -> List[str]:
    """Split a single block that is larger than chunk_size on sentence boundaries."""
    sentences = [s.strip() for s in text.replace("\n", " ").split(". ") if s.strip()]
    chunks: List[str] = []
    current = ""
    for sentence in sentences:
        full_sentence = sentence if sentence.endswith(".") else sentence + "."
        if len(current) + len(full_sentence) + 1 <= chunk_size:
            current = (current + " " + full_sentence).strip()
        else:
            if current:
                chunks.append(current)
            overlap_text = _get_tail(current, overlap) if current else ""
            current = (overlap_text + " " + full_sentence).strip() if overlap_text else full_sentence
    if current:
        chunks.append(current)
    return chunks


def _get_tail(text: str, length: int) -> str:
    """Return the last `length` characters of text, trimmed to a word boundary."""
    if len(text) <= length:
        return text
    tail = text[-length:]
    # Trim to word boundary
    space_idx = tail.find(" ")
    if space_idx > 0:
        tail = tail[space_idx:].strip()
    return tail


# ---------------------------------------------------------------------------
# RegulationEmbedder
# ---------------------------------------------------------------------------

class RegulationEmbedder:
    """
    Manages chunking, embedding, and FAISS-based retrieval for regulation texts.

    Storage layout (under settings.VECTOR_DIR):
      regulation_index.faiss   – FAISS IndexFlatIP (normalized embeddings → cosine sim)
      regulation_meta.json     – List of per-chunk metadata dicts, ordered by FAISS position
    """

    def __init__(self):
        settings = get_settings()
        self._embed_service = get_embedding_service()
        self._vector_dir: Path = settings.VECTOR_DIR
        self._vector_dir.mkdir(parents=True, exist_ok=True)

        self._index_path = self._vector_dir / REGULATION_INDEX_FILENAME
        self._meta_path = self._vector_dir / REGULATION_META_FILENAME

        dim = self._embed_service.embedding_dim
        self._index: Any = self._load_or_create_index(dim)
        self._meta: List[Dict[str, Any]] = self._load_or_create_meta()

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _load_or_create_index(self, dim: int) -> Any:
        if self._index_path.exists():
            try:
                idx = faiss.read_index(str(self._index_path))
                if idx.d == dim:
                    print(f"[RegulationEmbedder] Loaded existing FAISS index ({idx.ntotal} vectors).")
                    return idx
            except Exception as e:
                print(f"[RegulationEmbedder] Could not load existing index ({e}), creating new.")
        print(f"[RegulationEmbedder] Creating new FAISS index (dim={dim}).")
        return faiss.IndexFlatIP(dim)

    def _load_or_create_meta(self) -> List[Dict[str, Any]]:
        if self._meta_path.exists():
            try:
                with open(self._meta_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[RegulationEmbedder] Could not load metadata ({e}), starting fresh.")
        return []

    def _persist(self):
        faiss.write_index(self._index, str(self._index_path))
        with open(self._meta_path, "w", encoding="utf-8") as f:
            json.dump(self._meta, f, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------
    # Embedding a single regulation
    # ------------------------------------------------------------------

    def embed_regulation(self, regulation: Regulation) -> int:
        """
        Chunk and embed a single Regulation object.

        Returns the number of new chunks embedded (0 if already embedded).
        """
        if not regulation.full_text:
            print(f"[RegulationEmbedder] Skipping '{regulation.short_name}' – no full_text.")
            return 0

        # Check if this regulation is already embedded
        already = [m for m in self._meta if m["regulation_id"] == regulation.id]
        if already:
            print(f"[RegulationEmbedder] '{regulation.short_name}' already embedded ({len(already)} chunks).")
            return 0

        chunks = _split_into_chunks(regulation.full_text)
        if not chunks:
            return 0

        print(f"[RegulationEmbedder] Embedding '{regulation.short_name}' → {len(chunks)} chunks…")

        embeddings = self._embed_service.embed_texts(chunks).astype("float32")

        start_idx = self._index.ntotal
        self._index.add(embeddings)

        for i, (chunk_text, _) in enumerate(zip(chunks, embeddings)):
            self._meta.append({
                "vector_idx": start_idx + i,
                "regulation_id": regulation.id,
                "regulation_name": regulation.name,
                "short_name": regulation.short_name,
                "jurisdiction": regulation.jurisdiction,
                "category": regulation.category,
                "chunk_index": i,
                "text": chunk_text,
            })

        self._persist()
        return len(chunks)

    # ------------------------------------------------------------------
    # Batch embedding (all regulations)
    # ------------------------------------------------------------------

    def embed_all_regulations(self, db: Session) -> Dict[str, Any]:
        """
        Embed every Regulation in the database that hasn't been embedded yet.

        Returns a summary dict.
        """
        regulations = db.query(Regulation).all()
        total_chunks = 0
        skipped = 0
        embedded_regs = 0

        for reg in regulations:
            n = self.embed_regulation(reg)
            if n > 0:
                total_chunks += n
                embedded_regs += 1
            else:
                skipped += 1

        return {
            "regulations_embedded": embedded_regs,
            "regulations_skipped": skipped,
            "total_chunks": total_chunks,
            "index_size": self._index.ntotal,
        }

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = 5,
        jurisdiction_filter: Optional[str] = None,
        regulation_id_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search the regulation index for chunks relevant to `query`.

        Args:
            query:                  Natural language query.
            top_k:                  Number of results to return.
            jurisdiction_filter:    If set, only return chunks from this jurisdiction.
            regulation_id_filter:   If set, only return chunks from this regulation.

        Returns:
            List of result dicts: {score, regulation_id, regulation_name,
                                   short_name, jurisdiction, chunk_index, text}
        """
        if self._index.ntotal == 0:
            return []

        query_vec = self._embed_service.embed_text(query).astype("float32")
        query_vec = np.expand_dims(query_vec, 0)

        # Fetch more candidates if filters are applied
        fetch_k = min(top_k * 4 if (jurisdiction_filter or regulation_id_filter) else top_k, self._index.ntotal)
        scores, indices = self._index.search(query_vec, fetch_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self._meta):
                continue
            meta = self._meta[idx]
            if jurisdiction_filter and meta.get("jurisdiction") != jurisdiction_filter:
                continue
            if regulation_id_filter and meta.get("regulation_id") != regulation_id_filter:
                continue
            results.append({
                "score": float(score),
                **meta,
            })
            if len(results) >= top_k:
                break

        return results

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def status(self) -> Dict[str, Any]:
        """Return current index statistics."""
        jurisdictions: Dict[str, int] = {}
        for m in self._meta:
            j = m.get("jurisdiction", "unknown")
            jurisdictions[j] = jurisdictions.get(j, 0) + 1
        return {
            "total_vectors": self._index.ntotal,
            "total_chunks": len(self._meta),
            "by_jurisdiction": jurisdictions,
        }

    def reset(self):
        """Clear the regulation index (used in tests or re-seeding)."""
        dim = self._embed_service.embedding_dim
        self._index = faiss.IndexFlatIP(dim)
        self._meta = []
        self._persist()
        print("[RegulationEmbedder] Index reset.")


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_regulation_embedder: Optional[RegulationEmbedder] = None


def get_regulation_embedder() -> RegulationEmbedder:
    global _regulation_embedder
    if _regulation_embedder is None:
        _regulation_embedder = RegulationEmbedder()
    return _regulation_embedder
