import logging
from typing import Dict, Any, List, Optional
from openai import OpenAI
from ..graph import get_graph_driver
from ..vectorstore import get_vector_store
from ..connectors import get_mcp_adapters
from ..config import settings

logger = logging.getLogger(__name__)

class BaseAgent:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.graph = get_graph_driver()
        self.vector_store = get_vector_store()
        self.mcp_adapters = get_mcp_adapters()
        self.openai_client = None
        self.is_gemini = False
        
        if settings.OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(
                    api_key=settings.OPENAI_API_KEY,
                    base_url=settings.OPENAI_API_BASE
                )
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        elif settings.GEMINI_API_KEY:
            try:
                self.openai_client = OpenAI(
                    api_key=settings.GEMINI_API_KEY,
                    base_url="https://generativelanguage.googleapis.com/v1beta/openai"
                )
                self.is_gemini = True
                logger.info(f"Initialized OpenAI client with Gemini compatibility layer for agent {self.name}")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client with Gemini: {e}")

    def call_llm(self, system_prompt: str, user_prompt: str, response_format: Optional[Dict[str, Any]] = None) -> str:
        """Call LLM if available, otherwise return empty string (subclasses handle fallback)."""
        if not self.openai_client:
            return ""
            
        try:
            model = settings.GEMINI_MODEL if self.is_gemini else settings.OPENAI_MODEL
            kwargs = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            }
            if response_format:
                kwargs["response_format"] = response_format
                
            response = self.openai_client.chat.completions.create(**kwargs)
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"LLM API Call failed in agent {self.name}: {e}")
            return ""
            
    def run(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Override in subclass. Should return a dictionary with keys:
        - "agent_name": str
        - "trace": List[str] (list of reasoning steps)
        - "result": Dict[str, Any] (actual agent output)
        """
        raise NotImplementedError
