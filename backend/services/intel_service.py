import logging
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from core.config import settings
from core.llm_factory import LLMFactory
from services.risk_scorer import risk_scorer
from services.qdrant_service import semantic_search

logger = logging.getLogger(__name__)

INTEL_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a Senior Global Regulatory Intelligence Analyst.
Analyze the provided regulation and provide a hard-hitting intelligence report.

AUTHENTICITY RULES:
1. **Explicit Jurisdiction**: State exactly where this regulation is from (mention Country/Region).
2. **Real Comparisons**: Use the 'CROSS-JURISDICTIONAL CONTEXT' provided to draw specific parallels with diverse global standards.
   - Contrast with at least two different jurisdictions if available in context.
   - If no specific legal parallels are found, focus on the operational impact for multinational companies.
3. **No Fluff**: Do not say "it may relate to." Say "This aligns with..." or "This differs from..."
4. **Impact Areas**: Identify exactly which departments (e.g., Legal, IT, HR, Finance) are affected.
"""),
    ("human", """
JURISDICTION: {jurisdiction}
REGULATION TITLE: {title}
REGULATION TEXT: {text}

CROSS-JURISDICTIONAL CONTEXT (Laws/Regulations from other regions):
{context}

Respond in JSON only:
{{
  "explanation": "Brief context including origin and purpose.",
  "comparison": "Evidence-based cross-reference with at least one global standard from the context.",
  "impact_areas": ["List of affected areas"],
  "risk_score": 1-10
}}"""),
])

class RegulationIntelligenceService:
    @staticmethod
    def _invoke_chain(chain, input_data):
        """Helper to invoke with factory-level fallback."""
        return chain.ainvoke(input_data)

    @staticmethod
    async def get_regulation_intel(title: str, text: str, jurisdiction: str = "Global") -> dict:
        """Generates structured intelligence for a regulation."""
        risk_score = risk_scorer.predict(text)
        
        # Perform cross-jurisdictional search with diversity weighting
        # We fetch a larger pool (top 50) and then pick representative examples 
        # from various jurisdictions to ensure the LLM sees a global spectrum.
        similar_regs = semantic_search(
            query_text=text[:1500], 
            top_k=50, 
            score_threshold=0.35, # Increased threshold to ensure strictly relevant cross-references
            source_type_filter="regulation"
        )
        
        # Diversity Filter: Pick the top record from each jurisdiction
        jurisdiction_map: Dict[str, Dict] = {}
        for reg in similar_regs:
            reg_juris = reg.get("jurisdiction", "Global")
            
            # Skip the country we are already analyzing to ensure cross-jurisdictional context
            if jurisdiction and reg_juris.lower() == jurisdiction.lower():
                continue 
            
            if reg_juris not in jurisdiction_map:
                jurisdiction_map[reg_juris] = reg
            
            if len(jurisdiction_map) >= 10: # Limit to top 10 distinct countries for contextual richness
                break
        
        other_juris_context = []
        for reg_juris, reg in jurisdiction_map.items():
            other_juris_context.append(
                f"REGION: {reg_juris}\nREGULATION: {reg.get('title')}\nPRELUDE: {reg.get('text')[:350]}..."
            )
        
        context_str = "\n\n---\n\n".join(other_juris_context) or "No diverse jurisdictional parallels found in local database."
        
        try:
            try:
                llm = LLMFactory.get_llm(provider="gemini")
                chain = INTEL_PROMPT | llm | StrOutputParser()
                logger.info(f"🧠 Generating Intelligence Profile for: {title[:50]}...")
                raw_response = await chain.ainvoke({
                    "title": title,
                    "text": text[:5000],
                    "jurisdiction": jurisdiction,
                    "context": context_str
                })
            except Exception as gemini_err:
                gemini_quota = "429" in str(gemini_err) or "quota" in str(gemini_err).lower() or "resource_exhausted" in str(gemini_err).lower()
                
                if gemini_quota and LLMFactory.is_key_valid(settings.groq_api_key):
                    logger.warning(f"⚠️ Gemini Quota Exceeded. Falling back to Groq...")
                    llm = LLMFactory.get_llm(provider="groq")
                    chain = INTEL_PROMPT | llm | StrOutputParser()
                    raw_response = await chain.ainvoke({
                        "title": title,
                        "text": text[:5000],
                        "jurisdiction": jurisdiction,
                        "context": context_str
                    })
                elif gemini_quota:
                     logger.error("❌ Gemini Quota Exceeded and no valid Groq fallback found.")
                     raise RuntimeError("AI Quota Exceeded. Please configure a fallback provider or wait for reset.")
                else:
                    raise gemini_err
            
            # Clean up JSON if LLM adds markdown blocks
            json_str = raw_response.strip().replace("```json", "").replace("```", "")
            import json
            intel = json.loads(json_str)
            
            intel["risk_score"] = risk_score
            return intel
        except Exception as e:
            logger.error(f"❌ Intelligence generation failed after all attempts: {e}")
            msg = "Detailed AI analysis temporarily unavailable"
            if "quota" in str(e).lower() or "resource_exhausted" in str(e).lower():
                msg = "AI Quota limit reached. Please wait a few minutes."
            elif "Connection error" in str(e):
                msg = "Connection error with AI provider. Check API Keys."
            
            return {
                "explanation": f"Regulatory document regarding {title}. {msg}.",
                "comparison": "Cross-reference with global standards is pending neural synchronization.",
                "impact_areas": ["General Compliance"],
                "risk_score": risk_score
            }
