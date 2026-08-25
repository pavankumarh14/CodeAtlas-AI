from typing import List, Dict, Any, Optional
import uuid
import re
import logging
from .base import BaseGraphDriver

logger = logging.getLogger(__name__)

class InMemoryGraphDriver(BaseGraphDriver):
    def __init__(self):
        # Maps node_id (string) -> dict of {id, labels, properties}
        self.nodes_db: Dict[str, Dict[str, Any]] = {}
        # List of dicts: {id, type, start_node_id, end_node_id, properties}
        self.rels_db: List[Dict[str, Any]] = []

    def connect(self) -> bool:
        logger.info("Initializing In-Memory Graph Driver (Fallback Mode).")
        return True

    def close(self) -> None:
        logger.info("In-Memory Graph Driver closed.")

    def _get_pk_value(self, label: str, properties: Dict[str, Any]) -> str:
        if label == "Requirement":
            return properties.get("req_id", "")
        elif label == "Incident":
            return properties.get("inc_id", "")
        elif label in ("Document", "Runbook"):
            return properties.get("title", "")
        return properties.get("name", "")

    def _get_node_by_name(self, label: str, name: str) -> Optional[Dict[str, Any]]:
        for node in self.nodes_db.values():
            if label in node["labels"]:
                pk_val = self._get_pk_value(label, node["properties"])
                if pk_val.lower() == name.lower():
                    return node
        return None

    def query(self, cypher: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        parameters = parameters or {}
        # Strip comments and clean whitespace
        clean_cypher = re.sub(r'//.*', '', cypher).strip()
        clean_cypher = re.sub(r'\s+', ' ', clean_cypher)
        
        logger.debug(f"InMemory query: {clean_cypher} with {parameters}")
        
        # 1. MATCH (n:LABEL) RETURN n
        match_all = re.search(r'MATCH\s+\(n:(\w+)\)\s+RETURN\s+n', clean_cypher, re.IGNORECASE)
        if match_all:
            label = match_all.group(1)
            nodes = self.get_nodes(label)
            # Neo4j python driver returns objects that look like dicts, or node structures.
            # We mock the node object. We can mock it as an object with element_id, labels, and dict interface
            return [{"n": MockNeo4jNode(node["id"], node["labels"], node["properties"])} for node in nodes]
            
        # 2. MATCH (n) DETACH DELETE n
        if "DETACH DELETE" in clean_cypher.upper():
            self.clear()
            return []

        # 3. Specific query handlers for the Agents
        # Dependency chains or incidents matching can be emulated based on incoming cypher
        if "DEPENDS_ON" in clean_cypher or "USES" in clean_cypher:
            # Check for service dependency query
            service_name = parameters.get("service_name")
            if service_name:
                direction = "upstream" if "->" in clean_cypher else "downstream"
                paths = self.get_dependency_chain(service_name, direction)
                # Map to format expected by Neo4j path parser
                # path return format: [{"path": MockNeo4jPath(path)}]
                return [{"path": MockNeo4jPath(p["nodes"], p["relationships"])} for p in paths]

        # General node lookup by properties
        # MATCH (n:Label {pk: $val}) RETURN n
        match_node_pk = re.search(r'MATCH\s+\(n:(\w+)\s+\{(\w+):\s*(\$\w+)\}\)', clean_cypher)
        if match_node_pk:
            label = match_node_pk.group(1)
            prop = match_node_pk.group(2)
            param_key = match_node_pk.group(3)[1:]
            target_val = parameters.get(param_key)
            
            node = self._get_node_by_name(label, str(target_val))
            if node:
                return [{"n": MockNeo4jNode(node["id"], node["labels"], node["properties"])}]
            return []

        # If it doesn't match predefined regexes, return empty list or log
        logger.warning(f"In-Memory Graph Query not fully simulated: {clean_cypher}")
        return []

    def get_nodes(self, label: Optional[str] = None) -> List[Dict[str, Any]]:
        if not label:
            return list(self.nodes_db.values())
        return [node for node in self.nodes_db.values() if label in node["labels"]]

    def get_relationships(self, rel_type: Optional[str] = None) -> List[Dict[str, Any]]:
        results = []
        for rel in self.rels_db:
            if rel_type and rel["type"] != rel_type:
                continue
            
            start_node = self.nodes_db.get(rel["start_node_id"])
            end_node = self.nodes_db.get(rel["end_node_id"])
            
            if start_node and end_node:
                results.append({
                    "id": rel["id"],
                    "type": rel["type"],
                    "start_node": {
                        "id": start_node["id"],
                        "name": self._get_pk_value(start_node["labels"][0], start_node["properties"]),
                        "labels": start_node["labels"]
                    },
                    "end_node": {
                        "id": end_node["id"],
                        "name": self._get_pk_value(end_node["labels"][0], end_node["properties"]),
                        "labels": end_node["labels"]
                    },
                    "properties": rel["properties"]
                })
        return results

    def get_neighbors(self, name: str, label: str) -> List[Dict[str, Any]]:
        center_node = self._get_node_by_name(label, name)
        if not center_node:
            return []
        
        neighbors = []
        center_id = center_node["id"]
        
        for rel in self.rels_db:
            target_id = None
            is_start = False
            
            if rel["start_node_id"] == center_id:
                target_id = rel["end_node_id"]
                is_start = True
            elif rel["end_node_id"] == center_id:
                target_id = rel["start_node_id"]
                is_start = False
                
            if target_id:
                neigh_node = self.nodes_db.get(target_id)
                if neigh_node:
                    neighbors.append({
                        "relationship": {
                            "type": rel["type"],
                            "properties": rel["properties"]
                        },
                        "node": {
                            "id": neigh_node["id"],
                            "labels": neigh_node["labels"],
                            "name": self._get_pk_value(neigh_node["labels"][0], neigh_node["properties"]),
                            "properties": neigh_node["properties"]
                        }
                    })
        return neighbors

    def get_dependency_chain(self, service_name: str, direction: str = "downstream") -> List[Dict[str, Any]]:
        # Service dependency finder using BFS
        start_node = self._get_node_by_name("Service", service_name)
        if not start_node:
            return []
            
        start_id = start_node["id"]
        visited = set()
        paths = []
        
        # We want to trace paths
        # Queue stores (current_node_id, list_of_nodes_in_path, list_of_rels_in_path)
        from collections import deque
        queue = deque([(start_id, [start_node], [])])
        
        while queue:
            curr_id, path_nodes, path_rels = queue.popleft()
            
            # Find next relationships
            for rel in self.rels_db:
                # Upstream: Service -> DEPENDS_ON/USES -> Service (outgoing)
                # Downstream: Service <- DEPENDS_ON/USES - Service (incoming)
                next_id = None
                if direction == "upstream" and rel["start_node_id"] == curr_id:
                    if rel["type"] in ("DEPENDS_ON", "USES"):
                        next_id = rel["end_node_id"]
                elif direction == "downstream" and rel["end_node_id"] == curr_id:
                    if rel["type"] in ("DEPENDS_ON", "USES"):
                        next_id = rel["start_node_id"]
                        
                if next_id and next_id not in visited:
                    next_node = self.nodes_db.get(next_id)
                    if next_node and "Service" in next_node["labels"]:
                        new_nodes = path_nodes + [next_node]
                        new_rels = path_rels + [rel]
                        visited.add(next_id)
                        queue.append((next_id, new_nodes, new_rels))
                        
                        # Add to final paths
                        paths.append({
                            "nodes": [
                                {
                                    "id": n["id"],
                                    "labels": n["labels"],
                                    "name": n["properties"].get("name"),
                                    "properties": n["properties"]
                                } for n in new_nodes
                            ],
                            "relationships": [
                                {
                                    "id": r["id"],
                                    "type": r["type"],
                                    "start_node_id": r["start_node_id"],
                                    "end_node_id": r["end_node_id"],
                                    "properties": r["properties"]
                                } for r in new_rels
                            ]
                        })
        return paths

    def add_node(self, label: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        pk_val = self._get_pk_value(label, properties)
        node_id = f"{label}:{pk_val}"
        
        if node_id in self.nodes_db:
            # Update properties
            self.nodes_db[node_id]["properties"].update(properties)
        else:
            self.nodes_db[node_id] = {
                "id": node_id,
                "labels": [label],
                "properties": properties
            }
        return self.nodes_db[node_id]

    def add_relationship(self, source_label: str, source_name: str, 
                         target_label: str, target_name: str, 
                         rel_type: str, properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        src_node = self._get_node_by_name(source_label, source_name)
        tgt_node = self._get_node_by_name(target_label, target_name)
        
        if not src_node:
            logger.warning(f"Source node {source_label}:{source_name} not found.")
            return {}
        if not tgt_node:
            logger.warning(f"Target node {target_label}:{target_name} not found.")
            return {}
            
        src_id = src_node["id"]
        tgt_id = tgt_node["id"]
        
        # Check if relation already exists
        existing_rel = None
        for rel in self.rels_db:
            if rel["start_node_id"] == src_id and rel["end_node_id"] == tgt_id and rel["type"] == rel_type:
                existing_rel = rel
                break
                
        props = properties or {}
        if existing_rel:
            existing_rel["properties"].update(props)
            return existing_rel
        else:
            new_rel = {
                "id": str(uuid.uuid4()),
                "type": rel_type,
                "start_node_id": src_id,
                "end_node_id": tgt_id,
                "properties": props
            }
            self.rels_db.append(new_rel)
            return new_rel

    def clear(self) -> None:
        self.nodes_db.clear()
        self.rels_db.clear()
        logger.info("Cleared entire In-Memory database.")

class MockNeo4jNode:
    """Helper class to mock Neo4j's Node object return structure."""
    def __init__(self, element_id: str, labels: List[str], properties: Dict[str, Any]):
        self.element_id = element_id
        self.labels = set(labels)
        self._properties = properties

    def __getitem__(self, key):
        return self._properties[key]

    def get(self, key, default=None):
        return self._properties.get(key, default)

    def keys(self):
        return self._properties.keys()

    def values(self):
        return self._properties.values()

    def items(self):
        return self._properties.items()

    def __iter__(self):
        return iter(self._properties)

class MockNeo4jPath:
    """Helper class to mock Neo4j's Path object return structure."""
    def __init__(self, nodes: List[Dict[str, Any]], relationships: List[Dict[str, Any]]):
        self.nodes = [MockNeo4jNode(n["id"], n["labels"], n["properties"]) for n in nodes]
        self.relationships = [MockNeo4jRel(r["id"], r["type"], r["start_node_id"], r["end_node_id"], r["properties"]) for r in relationships]

class MockNeo4jRel:
    """Helper class to mock Neo4j's Relationship object return structure."""
    def __init__(self, element_id: str, rel_type: str, start_node_id: str, end_node_id: str, properties: Dict[str, Any]):
        self.element_id = element_id
        self.type = rel_type
        self.properties = properties
        self.start_node = MockNeo4jNodeRef(start_node_id)
        self.end_node = MockNeo4jNodeRef(end_node_id)

    def __getitem__(self, key):
        return self.properties[key]

    def get(self, key, default=None):
        return self.properties.get(key, default)

class MockNeo4jNodeRef:
    def __init__(self, element_id: str):
        self.element_id = element_id
