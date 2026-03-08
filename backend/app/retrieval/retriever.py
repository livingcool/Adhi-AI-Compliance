from typing import List, Optional, Tuple, Dict, Any, Set
import numpy as np
from app.api.schemas import QueryRequest, SourceChunk
from app.services.embedder import get_embedding_service
from app.store.vector_store import get_vector_store
from app.store.metadata_store import get_db, TextChunk, Document, Organization, get_organization_by_slug
from sqlalchemy.orm import joinedload


class Retriever:
    """
    Core service responsible for retrieving the most relevant text chunks 
    using hybrid (FAISS/Supabase) storage.
    """

    def __init__(self):
        self.embedder = get_embedding_service()
        self.vector_store = get_vector_store()
    
    def retrieve_chunks(self, request: QueryRequest) -> List[SourceChunk]:
        """
        Processes the query and searches the vector index for relevant chunks.
        """
        print(f"[Retriever] Received query: '{request.query}' for org: {request.organization_id}")
        
        # Run the core retrieval logic
        source_chunks, max_score = self._run_retrieval_cycle(
            request.query, 
            request.top_k, 
            request.organization_id
        )
        
        print(f"[Retriever] Retrieved {len(source_chunks)} chunks. Max score: {max_score:.4f}")
        return source_chunks

    def _run_retrieval_cycle(self, query: str, top_k: int, organization_id: str) -> Tuple[List[SourceChunk], float]:
        """Encapsulates the core embedding and database lookup logic."""
        
        # 0. Resolve Organization UUID (Crucial for Supabase/pgvector)
        org_uuid = None
        with get_db() as db:
            org = get_organization_by_slug(db, organization_id)
            if org:
                org_uuid = org.id
            else:
                # If org doesn't exist yet, we can't retrieve anything
                # Fallback to organization_id as UUID if possible (for direct UUID passing)
                try:
                    uuid.UUID(organization_id)
                    org_uuid = organization_id
                except:
                    print(f"[Retriever] Warning: Organization '{organization_id}' not found.")
                    return [], 0.0

        # 1. Embed the query
        query_vector = self.embedder.embed_text(query)
        
        # 2. Search the Vector Store (FAISS or Supabase)
        # Note: org_uuid is used for Supabase, organization_id (slug) for FAISS
        search_org_id = org_uuid if self.vector_store.use_supabase else organization_id
        distances, ids = self.vector_store.search(query_vector, top_k, search_org_id)
        
        if len(ids) == 0:
            print("[Retriever] No valid results found in vector store.")
            return [], 0.0

        score_map: Dict[Any, float] = {}
        max_score = 0.0
        
        # Convert distances to scores
        # In FAISS mode, distances are IP (higher is better). In Supabase, search returns similarity (0-1).
        for i, vid in enumerate(ids):
            if vid is not None:
                score = float(distances[i])
                score_map[vid] = score
                max_score = max(max_score, score)

        # 3. Retrieve metadata from the SQL DB
        print(f"[Retriever] Retrieving metadata for {len(ids)} vectors...")
        
        with get_db(org_id=org_uuid) as db:
            # Handle both local-style (int vector_id) and supabase-style (uuid chunk_id)
            if self.vector_store.use_supabase:
                # Query by TextChunk ID directly (since Supabase search returns these)
                metadata_chunks: List[TextChunk] = (
                    db.query(TextChunk)
                    .join(TextChunk.document)
                    .join(Document.organization)
                    .filter(TextChunk.id.in_(ids.tolist()))
                    .options(joinedload(TextChunk.document).joinedload(Document.organization))
                    .all()
                )
            else:
                # Local FAISS style (by vector_id)
                metadata_chunks: List[TextChunk] = (
                    db.query(TextChunk)
                    .join(TextChunk.document)
                    .join(Document.organization)
                    .filter(TextChunk.vector_id.in_([int(v) for v in ids]))
                    .filter(Organization.slug == organization_id)
                    .options(joinedload(TextChunk.document).joinedload(Document.organization))
                    .all()
                )
            
            # --- FIGURE LINKING LOGIC ---
            mentioned_figure_ids: Set[str] = set()
            for chunk in metadata_chunks:
                if chunk.figure_ids:
                    ids_list = [fid.strip() for fid in chunk.figure_ids.split(',')]
                    mentioned_figure_ids.update(ids_list)
            
            linked_image_chunks: List[TextChunk] = []
            if mentioned_figure_ids:
                print(f"[Retriever] Found figure references: {mentioned_figure_ids}")
                for fig_id in mentioned_figure_ids:
                    found_images = (
                        db.query(TextChunk)
                        .join(TextChunk.document)
                        .join(Document.organization)
                        .filter(Organization.slug == organization_id)
                        .filter(TextChunk.chunk_type == "image")
                        .filter(TextChunk.figure_ids.like(f"%{fig_id}%"))
                        .all()
                    )
                    linked_image_chunks.extend(found_images)
            
            seen_ids = {c.id for c in metadata_chunks}
            final_chunks = list(metadata_chunks)
            
            for img_chunk in linked_image_chunks:
                if img_chunk.id not in seen_ids:
                    final_chunks.append(img_chunk)
                    seen_ids.add(img_chunk.id)
                    score_map[img_chunk.id] = max_score
        
        # 4. Assemble final SourceChunk list
        RELEVANCE_THRESHOLD = 0.5 # Lowered for development breadth
        
        source_chunks: List[SourceChunk] = []
        for chunk in final_chunks:
            # Identifer lookup depends on backend
            lookup_key = chunk.id if self.vector_store.use_supabase else chunk.vector_id
            score = score_map.get(lookup_key, 0.0)
            
            if score < RELEVANCE_THRESHOLD and chunk.chunk_type != "image":
                continue
                
            # Construct a reachable URL for the frontend if an image exists
            image_url = None
            if chunk.image_path:
                source_id = chunk.document.source_id
                filename = Path(chunk.image_path).name
                # This matches the route in routes_static.py
                image_url = f"/api/v1/static/images/{source_id}/{filename}"

            source_chunks.append(
                SourceChunk(
                    source_file=chunk.document.source_file_name,
                    chunk_text=chunk.text_content,
                    start_time=chunk.start_time,
                    end_time=chunk.end_time,
                    score=score,
                    metadata={
                        "document_id": chunk.document_id, 
                        "organization": chunk.document.organization.name,
                        "page_number": chunk.page_number
                    },
                    image_path=image_url,
                    chunk_type=chunk.chunk_type or "text",
                    figure_ids=chunk.figure_ids
                )
            )
            
        source_chunks.sort(key=lambda x: x.score, reverse=True)
        return source_chunks, max_score


# --- Singleton setup ---
_retriever: Optional[Retriever] = None

def get_retriever() -> Retriever:
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever