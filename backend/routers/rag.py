from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.rag_pipeline import rag_question_answer
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class RAGQuery(BaseModel):
    question: str

@router.post("/explain")
async def explain_regulation(payload: RAGQuery):
    """Natural language Q&A over the regulation knowledge base."""
    try:
        return await rag_question_answer(payload.question)
    except Exception as e:
        logger.error(f"Error in explain_regulation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis engine error: {str(e)}")
