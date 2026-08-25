import logging
from .base import BaseVectorStore
from .chroma_driver import ChromaVectorStore
from .in_memory_driver import InMemoryVectorStore
from ..config import settings

logger = logging.getLogger(__name__)

# Cached vector store instance (Singleton pattern)
_vector_store_instance = None

def get_vector_store() -> BaseVectorStore:
    global _vector_store_instance
    if _vector_store_instance is not None:
        return _vector_store_instance

    if settings.FORCE_FALLBACK:
        logger.info("Force Fallback enabled. Starting In-Memory Vector Store...")
        _vector_store_instance = InMemoryVectorStore()
        _vector_store_instance.connect()
        return _vector_store_instance

    # Try ChromaDB first
    logger.info("Attempting connection to ChromaDB...")
    chroma_store = ChromaVectorStore()
    if chroma_store.connect():
        _vector_store_instance = chroma_store
    else:
        logger.warning("ChromaDB connection failed. Falling back to In-Memory Vector Store.")
        _vector_store_instance = InMemoryVectorStore()
        _vector_store_instance.connect()
        
    return _vector_store_instance
