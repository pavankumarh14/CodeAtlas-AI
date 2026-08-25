import math
import re
from typing import List, Dict, Any, Set, Optional
import logging
from .base import BaseVectorStore

logger = logging.getLogger(__name__)

class InMemoryVectorStore(BaseVectorStore):
    def __init__(self):
        # List of dicts: {"id": str, "text": str, "metadata": dict}
        self.documents: List[Dict[str, Any]] = []

    def connect(self) -> bool:
        logger.info("Initializing In-Memory Vector Store (Fallback Mode).")
        return True

    def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]], ids: List[str]) -> None:
        for text, metadata, doc_id in zip(texts, metadatas, ids):
            # Check if id already exists, if so, replace it
            self.documents = [doc for doc in self.documents if doc["id"] != doc_id]
            self.documents.append({
                "id": doc_id,
                "text": text,
                "metadata": metadata
            })
        logger.debug(f"Added {len(texts)} documents to In-Memory Vector Store.")

    def _tokenize(self, text: str) -> List[str]:
        # Lowers and extracts alphanumeric words
        words = re.findall(r'\b\w+\b', text.lower())
        return words

    def _compute_tf(self, tokens: List[str]) -> Dict[str, int]:
        tf = {}
        for token in tokens:
            tf[token] = tf.get(token, 0) + 1
        return tf

    def _cosine_similarity(self, vec1: Dict[str, int], vec2: Dict[str, int]) -> float:
        intersection = set(vec1.keys()) & set(vec2.keys())
        if not intersection:
            return 0.0
        
        numerator = sum([vec1[x] * vec2[x] for x in intersection])
        
        sum1 = sum([vec1[x]**2 for x in vec1.keys()])
        sum2 = sum([vec2[x]**2 for x in vec2.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)
        
        if not denominator:
            return 0.0
        return float(numerator) / denominator

    def similarity_search(self, query: str, k: int = 3, metadata_filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        documents = self.documents
        if metadata_filter:
            documents = [
                doc for doc in documents
                if all(
                    (key in doc["metadata"] and doc["metadata"].get(key) != value.get("$ne") if isinstance(value, dict) and "$ne" in value
                     else doc["metadata"].get(key) == value)
                    for key, value in metadata_filter.items()
                )
            ]
        query_tokens = self._tokenize(query)
        if not query_tokens:
            # If query is empty, return top k arbitrary documents
            return [{
                "id": doc["id"],
                "text": doc["text"],
                "metadata": doc["metadata"],
                "score": 0.0
            } for doc in documents[:k]]
            
        query_tf = self._compute_tf(query_tokens)
        
        results = []
        for doc in documents:
            doc_tokens = self._tokenize(doc["text"])
            doc_tf = self._compute_tf(doc_tokens)
            similarity = self._cosine_similarity(query_tf, doc_tf)
            results.append({
                "id": doc["id"],
                "text": doc["text"],
                "metadata": doc["metadata"],
                "score": similarity
            })
            
        # Sort by similarity score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:k]

    def clear(self) -> None:
        self.documents.clear()
        logger.info("In-Memory Vector Store cleared.")
