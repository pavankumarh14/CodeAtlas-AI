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
    
    # Freshservice Settings
    FRESHSERVICE_DOMAIN: str = os.getenv("FRESHSERVICE_DOMAIN", "freshworks065.freshservice.com")
    FRESHSERVICE_API_KEY: str = os.getenv("FRESHSERVICE_API_KEY", "")
    FRESHSERVICE_WORKSPACE_ID: str = os.getenv("FRESHSERVICE_WORKSPACE_ID", "")
    # Shared secret the Workflow Automator webhook must send in the X-CodeAtlas-Secret header
    FRESHSERVICE_WEBHOOK_SECRET: str = os.getenv("FRESHSERVICE_WEBHOOK_SECRET", "")

    # GitHub change tracking for incident diagnosis (token optional: raises rate limit from 60 to 5000 req/hour)
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    GITHUB_CHANGE_WINDOW_DAYS: int = int(os.getenv("GITHUB_CHANGE_WINDOW_DAYS", "14"))
    
    # Fallback configuration
    FORCE_FALLBACK: bool = os.getenv("FORCE_FALLBACK", "false").lower() in ("true", "1", "yes")
    AUTO_SEED: bool = os.getenv("AUTO_SEED", "true").lower() in ("true", "1", "yes")

settings = Settings()
