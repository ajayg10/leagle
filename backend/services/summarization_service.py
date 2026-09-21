import logging
import json
from typing import List, Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from core.config import settings
from core.llm_factory import LLMFactory

logger = logging.getLogger(__name__)

SUMMARIZATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a senior legal and compliance analyst. 
Your task is to summarize complex regulatory documents or corporate filings into concise, information-dense summaries.
Focus on regulatory requirements, compliance obligations, risk factors, and financial impact.
Keep the summary around 500-800 words, but ensure it captures all critical compliance keywords and entities."""),
    ("human", """TITLE: {title}
SOURCE: {source}
CONTENT:
{text}

Generate a comprehensive compliance summary:"""),
])

class SummarizationService:
    @staticmethod
    def _get_llm():
        """Get LLM with fallback via LLMFactory."""
        return LLMFactory.get_llm(temperature=0)

    @staticmethod
    async def summarize_document(text: str, title: str = "", source: str = "") -> str:
        """
        Summarize a long document using Gemini.
        If the document is extremely long, it takes the first 20,000 characters
        as a representative sample to avoid context limits or excessive costs, 
        or you could implement sliding window summarization.
        """
        if not text or len(text) < 2000:
            return text  # Already short enough

        try:
            try:
                llm = SummarizationService._get_llm()
                chain = SUMMARIZATION_PROMPT | llm | StrOutputParser()
                sample_text = text[:30000] 
                logger.info(f"🔄 Summarizing document: {title[:50]}...")
                summary = await chain.ainvoke({
                    "title": title,
                    "source": source,
                    "text": sample_text,
                })
                return summary.strip()
            except Exception as e:
                if "429" in str(e) or "quota" in str(e).lower() or "resource_exhausted" in str(e).lower():
                    logger.warning(f"⚠️ Gemini Quota Exhausted! Falling back to Groq for Summarization...")
                    fallback_llm = LLMFactory.get_llm(provider="groq", temperature=0)
                    chain = SUMMARIZATION_PROMPT | fallback_llm | StrOutputParser()
                    summary = await chain.ainvoke({
                        "title": title,
                        "source": source,
                        "text": text[:30000],
                    })
                    return summary.strip()
                raise e
            logger.error(f"❌ Summarization failed: {e}")
            return text[:5000] # Fallback to truncation if LLM fails
