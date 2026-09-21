import logging
import json
from groq import Groq
from core.config import settings
from typing import Dict, Any

logger = logging.getLogger(__name__)

def extract_regulatory_entities(text: str) -> Dict[str, Any]:
    """
    Uses LLM to extract deterministic entities from regulatory text.
    Extracts: effective_date (YYYY-MM-DD), penalty_description, legal_weight (1-10).
    """
    if not settings.groq_api_key:
        logger.warning("GROQ_API_KEY not set. Skipping entity extraction.")
        return {}

    client = Groq(api_key=settings.groq_api_key)
    
    prompt = f"### [Instruction]: Extract the following entities from the regulatory text in JSON format:\n" \
             f"1. effective_date (YYYY-MM-DD format, or null if not found)\n" \
             f"2. penalty_description (Summary of fines/penalties, or null if none)\n" \
             f"3. legal_weight (1-10 scale: Constitution=10, Law/Act=7, Regulation/Ordinance=4, Advisory=1)\n" \
             f"4. category (one of: data_privacy, financial, environmental, healthcare, security, labor, compliance)\n\n" \
             f"### [Text]:\n{text[:4000]}\n\n" \
             f"### [Output JSON]:"

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        data = json.loads(completion.choices[0].message.content)
        logger.info(f"✅ Extracted Entities: {data}")
        return data
    except Exception as e:
        logger.error(f"❌ Entity Extraction Failed: {e}")
        return {}
