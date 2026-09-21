from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from models.policy import Policy
from services.ingestion import ingest_policy
from services.qdrant_service import semantic_search

router = APIRouter()

class PolicyIngestRequest(BaseModel):
    title: str
    content: str
    department: str
    owner: str

@router.post("/ingest", status_code=201)
async def create_policy(
    payload: PolicyIngestRequest,
    db: AsyncSession = Depends(get_db),
):
    """Ingest a company policy -> embed -> Qdrant"""
    policy = await ingest_policy(
        db=db,
        title=payload.title,
        content=payload.content,
        department=payload.department,
        owner=payload.owner
    )
    return {"id": str(policy.id), "title": policy.title}

@router.get("/")
async def list_policies(db: AsyncSession = Depends(get_db)):
    """List all ingested policies."""
    from sqlalchemy import select
    result = await db.execute(select(Policy).order_by(Policy.title))
    policies = result.scalars().all()
    return [
        {
            "id": str(p.id),
            "title": p.title,
            "department": p.department,
            "owner": p.owner,
            "created_at": p.created_at.isoformat() if p.created_at else None
        }
        for p in policies
    ]

@router.post("/{policy_id}/compliance-check")
async def compliance_check(policy_id: str, db: AsyncSession = Depends(get_db)):
    """
    Analyze policy against relevant regulations.
    Returns compliance score and gaps.
    """
    try:
        from core.database import get_db
        from sqlalchemy import select
        result = await db.execute(select(Policy).where(Policy.id == policy_id))
        policy = result.scalar_one_or_none()
        
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        # Find applicable regulations using semantic search
        similar_regulations = semantic_search(
            query_text=policy.content,
            top_k=10,
            score_threshold=0.3,
            source_type_filter="regulation"
        )
        
        # Placeholder for full RAG compliance checker 
        return {
            "policy_id": policy_id,
            "policy_title": policy.title,
            "compliance_score": 86,  # Placeholder
            "applicable_regulations": len(similar_regulations),
            "gaps": [
                "Review against recent DPDP act implications required"
            ],
            "status": "REQUIRES_REVIEW"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
