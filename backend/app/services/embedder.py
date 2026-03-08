import numpy as np
from typing import List, Optional
from app.config import Settings, get_settings

class EmbeddingService:
    """
    A service to handle the loading of the embedding model and
    the creation of text embeddings.
    
    LIGHTWEIGHT VERSION: Returns dummy embeddings to avoid heavy model loading
    """
    
    def __init__(self, settings: Settings):
        self.model_name = settings.EMBEDDING_MODEL
        self.device = 'cpu'  # No GPU needed for dummy embeddings
        print(f"[EmbeddingService] LIGHTWEIGHT MODE - Using dummy embeddings")
        
        # Standard embedding dimension (384 for all-MiniLM-L6-v2)
        self.embedding_dim = 384
        print(f"[EmbeddingService] Dummy embeddings enabled. Dimension: {self.embedding_dim}")

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Generates embeddings for a list of text chunks.
        
        Args:
            texts: A list of strings to embed.
            
        Returns:
            A numpy array of shape (num_texts, embedding_dim).
        """
        if not texts:
            return np.array([])
            
        print(f"[EmbeddingService] Generating DUMMY embeddings for {len(texts)} text chunks...")
        
        # Generate random embeddings and normalize them (LIGHTWEIGHT VERSION)
        num_texts = len(texts)
        embeddings = np.random.randn(num_texts, self.embedding_dim)
        
        # L2 normalization (same as real embeddings)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = embeddings / (norms + 1e-8)  # Avoid division by zero
        
        print(f"[EmbeddingService] Generated dummy embeddings with shape {embeddings.shape}")
        return embeddings

    def embed_text(self, text: str) -> np.ndarray:
        """
        Generates an embedding for a single text chunk.
        
        Args:
            text: A single string to embed.
            
        Returns:
            A 1D numpy array of shape (embedding_dim,).
        """
        # Get the 2D array (shape 1, dim) and return the first (only) row
        return self.embed_texts([text])[0]

# --- Singleton setup for Dependency Injection ---

_embedding_service: Optional[EmbeddingService] = None

def get_embedding_service() -> EmbeddingService:
    """
    Dependency injector for FastAPI to get a singleton EmbeddingService.
    """
    global _embedding_service
    if _embedding_service is None:
        settings = get_settings()
        _embedding_service = EmbeddingService(settings)
    return _embedding_service