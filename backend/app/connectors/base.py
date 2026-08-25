from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseMCPAdapter(ABC):
    @abstractmethod
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search the external source using the MCP interface."""
        pass

    @abstractmethod
    def fetch(self, item_id: str) -> Dict[str, Any]:
        """Fetch details for a specific item from the external source."""
        pass

    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        """Expose connector capabilities and credentials metadata."""
        pass

    @abstractmethod
    def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize external schema to CodeAtlas Living Ontology schema."""
        pass
