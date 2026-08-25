from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseVectorStore(ABC):
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection or initialize vector store."""
        pass

    @abstractmethod
    def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]], ids: List[str]) -> None:
        """Insert documents into the vector store."""
        pass

    @abstractmethod
    def similarity_search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Query vector store for top-k similar documents.
        Returns a list of dicts: {"id": str, "text": str, "metadata": dict, "score": float}
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all entries in the vector store."""
        pass
