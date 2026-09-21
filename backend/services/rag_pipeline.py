import logging
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from services.qdrant_service import semantic_search
from services.risk_service import RiskService
from core.config import settings

logger = logging.getLogger(__name__)

from langchain_nvidia_ai_endpoints import ChatNVIDIA
from core.llm_factory import LLMFactory
from core.config import settings

def _get_llm(temperature: float = 0.0, max_tokens: int = 512):
    """
    Returns the LLM for impact analysis.
    Prioritizes NVIDIA NIM if API key is available.
    """
    if settings.nvidia_api_key:
        return ChatNVIDIA(
            model="meta/llama-3.3-70b-instruct",
            api_key=settings.nvidia_api_key,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    return LLMFactory.get_llm(temperature=temperature, max_tokens=max_tokens)

IMPACT_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a senior compliance officer with expertise in cross-regulatory mapping.
Analyze the impact of a new regulation on an existing company policy by focusing on **CONTROL DOMAINS**.

CONTROL DOMAINS include:
- Access Control & Authentication
- Data Retention & Erasure
- Reporting & Breach Notification
- Audit Logging & Transparency
- Third-party/Vendor Risk
- Financial Disclosures & Evidence

ANALYSIS RULES:
1. **Domain Overlap**: Even if the regulation and policy have different high-level titles (e.g., "Nuclear Safeguards" vs "IT Access Policy"), if both mention **Access Control**, they ARE RELATED.
2. **Gap Detection**: If the regulation specifies a TECHNICAL DETAIL (e.g., "MFA mandatory", "Logs kept for 7 years", "24-hour reporting") and the policy is SILENT or LESS STRINGENT, mark this as **HIGH** or **MEDIUM** impact.
3. **Be Specific**: In `compliance_gaps`, quote the specific requirement from the regulation that is missing in the policy.
4. **Detailed Reasoning**: Provide a 400-500 character explanation of the friction between the two documents.
5. **JSON Response only**.

Response format:
{{
  "impact_level": "HIGH", "MEDIUM" or "LOW",
  "affected_clauses": ["Policy sections that must change or 'None-NewRequirement'"],
  "compliance_gaps": ["Detailed quotes of what the regulation requires that the policy lacks"],
  "recommended_actions": [
    {{"step": 1, "action": "Update clause X to include...", "deadline_days": 30, "owner": "CISO/Compliance"}}
  ],
  "compliance_deadline": "YYYY-MM-DD or null if not specified",
  "reasoning": "A deep-dive technical explanation of the compliance friction."
}}"""),
    ("human", """RELEVANT REGULATORY CONTEXT (retrieved from knowledge base):
{context}

NEW REGULATION:
{regulation_text}

EXISTING COMPANY POLICY TO ANALYZE:
{policy_text}

Analyze the impact and respond with JSON only."""),
])

SEMANTIC_SEARCH_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
    You are a Senior AI Compliance Officer and Legal Strategist. Your goal is to analyze the user's query against our Regulatory Database and provide a data-driven risk assessment.

    CONTEXT FROM DATABASE (Regulations & Legal Precedents):
    {context}

    USER QUERY:
    {question}

    INSTRUCTIONS:
    1. **Direct Answer**: Provide a concise answer based on the regulations found.
    2. **Precedent & Case Law**: Look for rows marked as [Legal Case] or [GDPR Case Study]. 
       - If a similar violation exists, cite it using this format: `> **Precedent**: Title of Case` (DO NOT wrap the title in extra brackets like `([title])`).
       - Explain the penalty or outcome.
    3. **Legal Citations**: When referencing a specific law, use: `(Ref: Law Name)`.
    4. **Actionable Remediation**: Suggest 1-3 specific steps.
    5. **Risk Score**: Estimate (Low, Medium, High).

    FORMATTING RULES:
    - Use `###` for headers.
    - **IMPORTANT**: ALWAYS put two empty lines (double newline) before every `###` header.
    - Use bold text for key terms.
    - Format response in professional Markdown.
    """),
    ("human", """QUESTION: {question}

Answer based on the context above:"""),
])

async def analyze_impact(
    regulation_text: str,
    policy_text: str,
    regulation_title: str = "",
    policy_title: str = "",
) -> dict:
    """
    Core RAG function: given a regulation and a policy,
    retrieve relevant context from Qdrant and use LLM to analyze impact.
    """
    similar_chunks = semantic_search(
        query_text=regulation_text,
        top_k=10, # More context
        score_threshold=0.15, # Even more sensitive
    )

    context = "\n\n---\n\n".join([
        f"Source: {chunk.get('title', 'Unknown')} (Category: {chunk.get('category', 'n/a')})\n{chunk['text']}"
        for chunk in similar_chunks
    ])

    if not context:
        context = "Analyze the primary texts provided below."

    try:
        llm = _get_llm(temperature=0.1, max_tokens=1000) 
        chain = IMPACT_ANALYSIS_PROMPT | llm | StrOutputParser()
        
        # LLMFactory now handles fallback internally via with_fallbacks
        raw_response = await LLMFactory.invoke_with_fallback(
            chain, 
            {
                "context": context,
                "regulation_text": f"{regulation_title}\n\n{regulation_text}"[:5000], 
                "policy_text": f"{policy_title}\n\n{policy_text}"[:6000], 
            }
        )

        clean = raw_response.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]

        result = json.loads(clean)
        result["source_chunks"] = [c["text"][:200] for c in similar_chunks]
        result["similarity_scores"] = [c["score"] for c in similar_chunks]
        return result

    except json.JSONDecodeError as e:
        logger.error(f"LLM returned invalid JSON: {raw_response[:500]}")
        return {
            "impact_level": "UNKNOWN",
            "compliance_gaps": ["Analysis failed — manual review required"],
            "recommended_actions": [],
            "compliance_deadline": None,
            "reasoning": f"Automated analysis failed: {str(e)}",
            "raw_response": raw_response,
        }

async def rag_question_answer(question: str) -> dict:
    """
    General RAG Q&A over the regulation knowledge base.
    """
    chunks = semantic_search(query_text=question, top_k=7, score_threshold=0.25)
    context = "\n\n---\n\n".join([
        f"Source: {c.get('title', 'Unknown')} (Category: {c.get('category', 'n/a')})\n{c['text']}"
        for c in chunks
    ])

    # Get Local ML prediction as a secondary anchor
    risk_service = RiskService()
    local_risk = risk_service.predict_risk(question)
    
    llm = _get_llm()
    chain = SEMANTIC_SEARCH_PROMPT | llm | StrOutputParser()

    # LLMFactory.get_llm() returns an LLM with automatic fallback to Groq
    answer = await LLMFactory.invoke_with_fallback(
        chain,
        {
            "context": context, 
            "question": f"{question} (Internal ML Signal: {local_risk})"
        }
    )

    return {
        "answer": answer,
        "local_ml_risk": local_risk,
        "sources": [{"title": c.get("title"), "score": c["score"]} for c in chunks],
    }
