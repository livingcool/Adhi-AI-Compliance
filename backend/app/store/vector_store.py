try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    faiss = None
    FAISS_AVAILABLE = False

import numpy as np
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any

from app.config import Settings, get_settings, StorageBackend
from app.services.embedder import EmbeddingService, get_embedding_service
from app.store.supabase_client import get_supabase_client

class VectorStore:
    """
    A service to manage vector search.
    Supports both local FAISS and Supabase pgvector.
    """
    
    def __init__(self, settings: Settings, embed_service: EmbeddingService):
        self.settings = settings
        self.embedding_dim = embed_service.embedding_dim
        self.use_supabase = settings.STORAGE_BACKEND == "supabase" or settings.SUPABASE_URL is not None
        
        if not self.use_supabase:
            print("[VectorStore] Using Local FAISS Storage")
            self.vector_dir = settings.VECTOR_DIR
            self.index_paths = {
                'pdf': self.vector_dir / "pdf_index.faiss",
                'audio': self.vector_dir / "audio_index.faiss",
                'video': self.vector_dir / "video_index.faiss",
                'image': self.vector_dir / "image_index.faiss"
            }
            self.indices: Dict[str, Any] = {}
            for file_type in self.index_paths.keys():
                self.indices[file_type] = self._load_or_create_index(file_type)
        else:
            print("[VectorStore] Using Supabase pgvector Storage")
            self.supabase = get_supabase_client()
        
    def _load_or_create_index(self, file_type: str) -> Any:
        index_path = self.index_paths[file_type]
        if index_path.exists():
            try:
                index = faiss.read_index(str(index_path))
                if index.d == self.embedding_dim:
                    return index
            except:
                pass
        return faiss.IndexFlatIP(self.embedding_dim)

    def add_vectors(self, vectors: np.ndarray, document_id: str, file_type: str = 'pdf') -> List[int]:
        """
        Adds vectors to the store. 
        In FAISS mode, returns dummy IDs.
        In Supabase mode, updates the text_chunks table.
        """
        if not vectors.any():
            return []
            
        vectors_f32 = vectors.astype('float32')
        
        if not self.use_supabase:
            index = self.indices.get(file_type, self.indices['pdf'])
            start_index = index.ntotal
            index.add(vectors_f32)
            return list(range(start_index, start_index + len(vectors)))
        else:
            # We don't use 'vector_id' in Supabase mode; we update the records directly via RPC or update
            # But the ingestor expects vector_ids. We'll return empty or similar to satisfy.
            # Real intelligence is stored in the embedding column of text_chunks.
            return [None] * len(vectors)

    def search_supabase(self, query_vector: np.ndarray, top_k: int, org_id: str) -> List[Dict[str, Any]]:
        """Searches Supabase using pgvector RPC."""
        if not self.use_supabase:
            return []
        
        rpc_params = {
            "query_embedding": query_vector.tolist(),
            "match_threshold": 0.5,
            "match_count": top_k,
            "org_id": org_id
        }
        
        response = self.supabase.rpc("match_text_chunks", rpc_params).execute()
        return response.data

    def search(self, query_vector: np.ndarray, top_k: int, organization_id: str, file_type: Optional[str] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Standardized search interface.
        If using Supabase, it returns scores and IDs formatted for the Retriever.
        """
        if query_vector.ndim == 1:
            query_vector = np.expand_dims(query_vector, axis=0)
            
        if not self.use_supabase:
            # Local FAISS search
            if file_type and file_type in self.indices:
                d, i = self.indices[file_type].search(query_vector.astype('float32'), top_k)
                return d[0], i[0]
            else:
                all_d, all_i = [], []
                for ft, idx in self.indices.items():
                    if idx.ntotal > 0:
                        d, i = idx.search(query_vector.astype('float32'), top_k)
                        all_d.append(d[0])
                        all_i.append(i[0])
                if not all_d: return np.array([]), np.array([])
                comb_d = np.concatenate(all_d)
                comb_i = np.concatenate(all_i)
                idx = np.argsort(comb_d)[::-1][:top_k]
                return comb_d[idx], comb_i[idx]
        else:
            # Supabase Search
            results = self.search_supabase(query_vector[0], top_k, organization_id)
            # Map back to distances/indices format for legacy compatibility or handle separately
            # Retriever now handles Supabase directly if we want, but let's return mock IDs 
            # and distances that represent scores.
            scores = np.array([r['score'] for r in results])
            # We use the text_chunks UUID as the identifier
            ids = np.array([r['id'] for r in results]) 
            return scores, ids

    def save_index(self):
        if not self.use_supabase:
            for ft, idx in self.indices.items():
                faiss.write_index(idx, str(self.index_paths[ft]))

# --- Singleton setup ---
_vector_store: Optional[VectorStore] = None

def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore(get_settings(), get_embedding_service())
    return _vector_store