from neo4j import GraphDatabase
from typing import List, Dict, Any, Optional
import logging
from .base import BaseGraphDriver

logger = logging.getLogger(__name__)

class Neo4jDriver(BaseGraphDriver):
    def __init__(self, uri: str, user: str, password: str):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None

    def connect(self) -> bool:
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Test connectivity
            self.driver.verify_connectivity()
            logger.info("Successfully connected to Neo4j database.")
            return True
        except Exception as e:
            logger.warning(f"Failed to connect to Neo4j at {self.uri}: {e}")
            self.driver = None
            return False

    def close(self) -> None:
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed.")

    def query(self, cypher: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if not self.driver:
            raise ConnectionError("Neo4j driver is not connected.")
        parameters = parameters or {}
        try:
            with self.driver.session() as session:
                result = session.run(cypher, parameters)
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Error executing Cypher query: {e}\nQuery: {cypher}")
            raise e

    def get_nodes(self, label: Optional[str] = None) -> List[Dict[str, Any]]:
        cypher = f"MATCH (n{':' + label if label else ''}) RETURN n"
        results = self.query(cypher)
        nodes = []
        for r in results:
            node = r['n']
            nodes.append({
                "id": node.element_id,
                "labels": list(node.labels),
                "properties": dict(node)
            })
        return nodes

    def get_relationships(self, rel_type: Optional[str] = None) -> List[Dict[str, Any]]:
        rel_clause = f"-[r:{rel_type}]->" if rel_type else "-[r]->"
        cypher = f"MATCH (s){rel_clause}(t) RETURN s, r, t"
        results = self.query(cypher)
        relationships = []
        for r in results:
            rel = r['r']
            relationships.append({
                "id": rel.element_id,
                "type": rel.type,
                "start_node": {
                    "id": r['s'].element_id,
                    "name": r['s'].get('name') or r['s'].get('title') or r['s'].get('req_id') or r['s'].get('inc_id'),
                    "labels": list(r['s'].labels)
                },
                "end_node": {
                    "id": r['t'].element_id,
                    "name": r['t'].get('name') or r['t'].get('title') or r['t'].get('req_id') or r['t'].get('inc_id'),
                    "labels": list(r['t'].labels)
                },
                "properties": dict(rel)
            })
        return relationships

    def get_neighbors(self, name: str, label: str) -> List[Dict[str, Any]]:
        cypher = f"""
        MATCH (n:{label} {{name: $name}})-[r]-(m)
        RETURN r, m
        """
        # If node doesn't have name, try title, req_id, or inc_id
        if label == "Requirement":
            cypher = """
            MATCH (n:Requirement {req_id: $name})-[r]-(m)
            RETURN r, m
            """
        elif label == "Incident":
            cypher = """
            MATCH (n:Incident {inc_id: $name})-[r]-(m)
            RETURN r, m
            """
        elif label == "Document":
            cypher = """
            MATCH (n:Document {title: $name})-[r]-(m)
            RETURN r, m
            """
        elif label == "Runbook":
            cypher = """
            MATCH (n:Runbook {title: $name})-[r]-(m)
            RETURN r, m
            """
            
        results = self.query(cypher, {"name": name})
        neighbors = []
        for r in results:
            rel = r['r']
            node = r['m']
            neighbors.append({
                "relationship": {
                    "type": rel.type,
                    "properties": dict(rel)
                },
                "node": {
                    "id": node.element_id,
                    "labels": list(node.labels),
                    "name": node.get('name') or node.get('title') or node.get('req_id') or node.get('inc_id'),
                    "properties": dict(node)
                }
            })
        return neighbors

    def get_dependency_chain(self, service_name: str, direction: str = "downstream") -> List[Dict[str, Any]]:
        # Downstream = services that depend on us, or services we impact
        # Upstream = services we depend on
        if direction == "downstream":
            cypher = """
            MATCH path = (s:Service {name: $service_name})<-[:DEPENDS_ON|USES*]-(dependent:Service)
            RETURN path
            """
        else:
            cypher = """
            MATCH path = (s:Service {name: $service_name})-[:DEPENDS_ON|USES*]->(dependency:Service)
            RETURN path
            """
        
        results = self.query(cypher, {"service_name": service_name})
        paths = []
        for r in results:
            path = r['path']
            # Convert Neo4j path to a serialized form
            serialized_nodes = []
            for n in path.nodes:
                serialized_nodes.append({
                    "id": n.element_id,
                    "labels": list(n.labels),
                    "name": n.get('name') or n.get('title'),
                    "properties": dict(n)
                })
            serialized_rels = []
            for rel in path.relationships:
                serialized_rels.append({
                    "id": rel.element_id,
                    "type": rel.type,
                    "start_node_id": rel.start_node.element_id,
                    "end_node_id": rel.end_node.element_id,
                    "properties": dict(rel)
                })
            paths.append({
                "nodes": serialized_nodes,
                "relationships": serialized_rels
            })
        return paths

    def add_node(self, label: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        # Merge on a primary key based on the label
        pk = "name"
        if label == "Requirement":
            pk = "req_id"
        elif label == "Incident":
            pk = "inc_id"
        elif label in ("Document", "Runbook"):
            pk = "title"

        cypher = f"""
        MERGE (n:{label} {{{pk}: $properties.{pk}}})
        SET n += $properties
        RETURN n
        """
        results = self.query(cypher, {"properties": properties})
        if results:
            node = results[0]['n']
            return {
                "id": node.element_id,
                "labels": list(node.labels),
                "properties": dict(node)
            }
        return {}

    def add_relationship(self, source_label: str, source_name: str, 
                         target_label: str, target_name: str, 
                         rel_type: str, properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        src_pk = "name"
        if source_label == "Requirement":
            src_pk = "req_id"
        elif source_label == "Incident":
            src_pk = "inc_id"
        elif source_label in ("Document", "Runbook"):
            src_pk = "title"

        tgt_pk = "name"
        if target_label == "Requirement":
            tgt_pk = "req_id"
        elif target_label == "Incident":
            tgt_pk = "inc_id"
        elif target_label in ("Document", "Runbook"):
            tgt_pk = "title"

        cypher = f"""
        MATCH (s:{source_label} {{{src_pk}: $src_name}})
        MATCH (t:{target_label} {{{tgt_pk}: $tgt_name}})
        MERGE (s)-[r:{rel_type}]->(t)
        SET r += $properties
        RETURN s, r, t
        """
        props = properties or {}
        results = self.query(cypher, {
            "src_name": source_name,
            "tgt_name": target_name,
            "properties": props
        })
        if results:
            rel = results[0]['r']
            return {
                "id": rel.element_id,
                "type": rel.type,
                "properties": dict(rel)
            }
        return {}

    def clear(self) -> None:
        cypher = "MATCH (n) DETACH DELETE n"
        self.query(cypher)
        logger.info("Cleared entire Neo4j database.")
