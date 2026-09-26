import logging
import asyncio
import os
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
        Creates an LLM instance with comprehensive multi-provider fallback.
        Assembles all available providers: Gemini -> Groq -> NVIDIA NIM.
        """
        target_provider = provider or settings.llm_provider
        gemini_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY", "")
        groq_key = settings.groq_api_key or os.getenv("GROQ_API_KEY", "")
        nvidia_key = settings.nvidia_api_key or os.getenv("NVIDIA_API_KEY", "")

        models = []

        # 1. Gemini primary and secondary
        if LLMFactory.is_key_valid(gemini_key):
            try:
                models.append(
                    ChatGoogleGenerativeAI(
                        model=settings.llm_model,
                        google_api_key=gemini_key,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        max_retries=1,
                    )
                )
            except Exception as e:
                logger.warning(f"Could not init Gemini primary: {e}")

            if settings.llm_model != "gemini-1.5-flash":
                try:
                    models.append(
                        ChatGoogleGenerativeAI(
                            model="gemini-1.5-flash",
                            google_api_key=gemini_key,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            max_retries=1,
                        )
                    )
                except Exception as e:
                    logger.warning(f"Could not init Gemini 1.5 flash: {e}")

        # 2. Groq Llama 3.3
        if LLMFactory.is_key_valid(groq_key):
            try:
                models.append(
                    ChatGroq(
                        model_name="llama-3.3-70b-versatile",
                        groq_api_key=groq_key,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                )
            except Exception as e:
                logger.warning(f"Could not init Groq: {e}")

        # 3. NVIDIA NIM Llama 3.3
        if LLMFactory.is_key_valid(nvidia_key):
            try:
                from langchain_nvidia_ai_endpoints import ChatNVIDIA
                models.append(
                    ChatNVIDIA(
                        model="meta/llama-3.3-70b-instruct",
                        api_key=nvidia_key,
                        temperature=temperature,
                        max_tokens=max_tokens or 1000,
                    )
                )
            except Exception as e:
                logger.warning(f"Could not init ChatNVIDIA: {e}")

        if not models:
            logger.warning("No live LLM API keys configured.")
            raise ValueError("No LLM API keys configured.")

        # If user explicitly preferred groq or nvidia, prioritize them
        if target_provider == "groq":
            groq_models = [m for m in models if isinstance(m, ChatGroq)]
            other_models = [m for m in models if not isinstance(m, ChatGroq)]
            models = groq_models + other_models
        elif target_provider == "nvidia":
            from langchain_nvidia_ai_endpoints import ChatNVIDIA
            nv_models = [m for m in models if isinstance(m, ChatNVIDIA)]
            other_models = [m for m in models if not isinstance(m, ChatNVIDIA)]
            models = nv_models + other_models

        primary = models[0]
        fallbacks = models[1:]
        if fallbacks:
            return primary.with_fallbacks(fallbacks)
        return primary

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
