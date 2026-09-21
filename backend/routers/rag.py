from fastapi import APIRouter
from pydantic import BaseModel
from services.rag_pipeline import rag_question_answer

router = APIRouter()

class RAGQuery(BaseModel):
    question: str

@router.post("/explain")
async def explain_regulation(payload: RAGQuery):
    """Natural language Q&A over the regulation knowledge base."""
    return await rag_question_answer(payload.question)
