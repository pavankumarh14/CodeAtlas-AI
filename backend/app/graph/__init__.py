import logging
from .base import BaseGraphDriver
from .neo4j_driver import Neo4jDriver
from .in_memory_driver import InMemoryGraphDriver
from ..config import settings

logger = logging.getLogger(__name__)

# Cached driver instance (Singleton pattern)
_driver_instance = None

def get_graph_driver() -> BaseGraphDriver:
    global _driver_instance
    if _driver_instance is not None:
        return _driver_instance

    if settings.FORCE_FALLBACK:
        logger.info("Force Fallback enabled. Starting in-memory graph driver...")
        _driver_instance = InMemoryGraphDriver()
        _driver_instance.connect()
        return _driver_instance

    # Try Neo4j first
    logger.info(f"Attempting connection to Neo4j at {settings.NEO4J_URI}...")
    neo4j_drv = Neo4jDriver(
        uri=settings.NEO4J_URI,
        user=settings.NEO4J_USER,
        password=settings.NEO4J_PASSWORD
    )
    if neo4j_drv.connect():
        _driver_instance = neo4j_drv
    else:
        logger.warning("Neo4j database connection failed. Falling back to In-Memory Graph Driver.")
        _driver_instance = InMemoryGraphDriver()
        _driver_instance.connect()
        
    return _driver_instance
