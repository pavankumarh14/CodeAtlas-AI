from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseGraphDriver(ABC):
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the graph database."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close connection to the graph database."""
        pass

    @abstractmethod
    def query(self, cypher: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a raw Cypher query and return the list of records."""
        pass

    @abstractmethod
    def get_nodes(self, label: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve all nodes, optionally filtered by ontology label."""
        pass

    @abstractmethod
    def get_relationships(self, rel_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve all relationships in the graph, optionally filtered by type."""
        pass

    @abstractmethod
    def get_neighbors(self, name: str, label: str) -> List[Dict[str, Any]]:
        """Get direct neighbors of a specific node."""
        pass

    @abstractmethod
    def get_dependency_chain(self, service_name: str, direction: str = "downstream") -> List[Dict[str, Any]]:
        """Get the dependency chain (blast radius or upstream dependencies) for a service."""
        pass

    @abstractmethod
    def add_node(self, label: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update a node in the graph."""
        pass

    @abstractmethod
    def add_relationship(self, source_label: str, source_name: str, 
                         target_label: str, target_name: str, 
                         rel_type: str, properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a relationship between two nodes."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear the entire database."""
        pass
