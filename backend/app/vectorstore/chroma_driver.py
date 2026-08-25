from typing import List, Dict, Any, Optional
import logging
from .base import BaseVectorStore

logger = logging.getLogger(__name__)

class ChromaVectorStore(BaseVectorStore):
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None

    def connect(self) -> bool:
        try:
            import chromadb
            # Instantiate Client
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            # Create or get collection
            self.collection = self.client.get_or_create_collection("codeatlas_docs")
            logger.info("Successfully connected to ChromaDB.")
            return True
        except ImportError:
            logger.warning("chromadb python package is not installed. ChromaVectorStore cannot be used.")
            return False
        except Exception as e:
            logger.warning(f"Failed to connect to ChromaDB: {e}")
            return False

    def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]], ids: List[str]) -> None:
        if not self.collection:
            raise ConnectionError("ChromaVectorStore is not connected.")
        # If chromadb doesn't receive embeddings, it will compute them using its default sentence-transformers model
        # To avoid heavy local model download during initial load, we can use basic representations or let Chroma compute them
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"Added {len(texts)} documents to ChromaDB.")

    def similarity_search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        if not self.collection:
            raise ConnectionError("ChromaVectorStore is not connected.")
        
        results = self.collection.query(
            query_texts=[query],
            n_results=k
        )
        
        formatted_results = []
        if results and 'documents' in results and results['documents']:
            docs = results['documents'][0]
            metas = results['metadatas'][0] if 'metadatas' in results and results['metadatas'] else [None] * len(docs)
            ids = results['ids'][0] if 'ids' in results and results['ids'] else [None] * len(docs)
            distances = results['distances'][0] if 'distances' in results and results['distances'] else [0.0] * len(docs)
            
            for doc, meta, doc_id, dist in zip(docs, metas, ids, distances):
                formatted_results.append({
                    "id": doc_id,
                    "text": doc,
                    "metadata": meta,
                    "score": float(1.0 - dist)  # convert distance to similarity score
                })
        return formatted_results

    def clear(self) -> None:
        if self.client and self.collection:
            self.client.delete_collection("codeatlas_docs")
            self.collection = self.client.get_or_create_collection("codeatlas_docs")
            logger.info("ChromaDB collection cleared.")
