import logging
import asyncio
from typing import List, Optional, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel
from core.config import settings

logger = logging.getLogger(__name__)

class LLMFactory:
    """
    Factory for creating LLM instances with automatic fallback logic.
    Primary: Gemini 2.0 Flash
    Fallback: Groq (llama-3.3-70b-versatile)
    """

    @staticmethod
    def is_key_valid(key: Optional[str]) -> bool:
        """Checks if a key is non-empty and doesn't look like a placeholder."""
        if not key or not isinstance(key, str):
            return False
        clean_key = key.strip()
        # Basic check for empty or just 'None' string
        if not clean_key or clean_key.lower() == "none" or len(clean_key) < 10:
            return False
        return True

    @staticmethod
    def get_llm(provider: str = None, temperature: float = 0.0, max_tokens: Optional[int] = None) -> BaseChatModel:
        """
        Creates an LLM instance for a specific provider with automatic fallback.
        """
        target_provider = provider or settings.llm_provider
        
        if target_provider == "groq":
            if not LLMFactory.is_key_valid(settings.groq_api_key):
                logger.error("❌ Groq API Key is missing or invalid.")
                raise ValueError("Groq API Key not configured.")
            
            return ChatGroq(
                model_name="llama-3.3-70b-versatile",
                groq_api_key=settings.groq_api_key,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        
        if target_provider == "nvidia":
            from langchain_nvidia_ai_endpoints import ChatNVIDIA
            return ChatNVIDIA(
                model=settings.llm_model if "nvidia" in settings.llm_model or "meta" in settings.llm_model else "meta/llama-3.3-70b-instruct",
                api_key=settings.nvidia_api_key,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        # Default: Gemini with Groq Fallback
        if not LLMFactory.is_key_valid(settings.gemini_api_key):
             logger.error("❌ Gemini API Key is missing or invalid.")
             if target_provider == "gemini":
                 raise ValueError("Gemini API Key not configured.")
        
        gemini = ChatGoogleGenerativeAI(
            model=settings.llm_model,
            google_api_key=settings.gemini_api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            max_retries=0, 
        )

        # Attach Groq as fallback if available
        if LLMFactory.is_key_valid(settings.groq_api_key):
            groq_fallback = ChatGroq(
                model_name="llama-3.3-70b-versatile",
                groq_api_key=settings.groq_api_key,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return gemini.with_fallbacks([groq_fallback])
        
        return gemini

    @staticmethod
    async def invoke_with_fallback(chain: Any, input_data: dict) -> Any:
        """
        Generic wrapper to catch quota errors and provide better logging,
        even though with_fallbacks handles the actual swap.
        """
        try:
            return await chain.ainvoke(input_data)
        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "quota" in error_str or "resource_exhausted" in error_str:
                logger.error(f"❌ ALL LLM providers exhausted quota: {str(e)}")
            raise e
