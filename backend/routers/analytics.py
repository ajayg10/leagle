from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.analytics_service import AnalyticsService
from services.qdrant_service import get_qdrant_client
from core.config import settings
from qdrant_client.models import Filter, FieldCondition, MatchValue
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class AnalyticsReport(BaseModel):
    document_id: str
    report: dict

@router.post("/compare/{filename}", response_model=AnalyticsReport)
async def compare_document(filename: str):
    """
    Triggers gap analysis for a previously uploaded document.
    """
    try:
        # 1. Fetch chunks from Qdrant for this document
        client = get_qdrant_client()
        response = client.query_points(
            collection_name=settings.qdrant_collection,
            query_filter=Filter(
                must=[
                    FieldCondition(key="filename", match=MatchValue(value=filename)),
                    FieldCondition(key="source_type", match=MatchValue(value="policy"))
                ]
            ),
            limit=100, # Analyze up to 100 chunks
            with_payload=True,
            with_vectors=False
        )
        
        chunks = [hit.payload.get("text", "") for hit in response.points]
        
        if not chunks:
            raise HTTPException(
                status_code=404,
                detail=f"No chunks found for document: {filename}. Ensure it was uploaded recently."
            )
            
        logger.info(f"📊 Running Gap Analysis for {filename} ({len(chunks)} chunks)")
        
        # 2. Run Analysis
        report = await AnalyticsService.compare_policy_to_regulations(chunks)
        
        return AnalyticsReport(document_id=filename, report=report)
        
    except HTTPException:
        raise
@router.get("/risk-heatmap")
async def get_risk_heatmap():
    """
    Returns aggregated risk data for the global heatmap (last 30 days).
    """
    try:
        data = await AnalyticsService.get_global_risk_heatmap()
        return data
    except Exception as e:
        logger.error(f"Failed to fetch risk heatmap: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate global risk metrics.")
