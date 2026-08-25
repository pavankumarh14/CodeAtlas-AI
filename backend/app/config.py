import os
from dotenv import load_dotenv

# Load env file if exists
load_dotenv()

class Settings:
    PROJECT_NAME: str = "CodeAtlas AI"
    API_V1_STR: str = "/api/v1"
    
    # Neo4j Settings
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password")
    
    # LLM Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_BASE: str = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Gemini Settings (Optional)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    # Fallback configuration
    FORCE_FALLBACK: bool = os.getenv("FORCE_FALLBACK", "false").lower() in ("true", "1", "yes")

settings = Settings()
