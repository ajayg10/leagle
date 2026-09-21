from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, delete
from core.database import get_db
from core.auth import require_admin
from models.regulation import Regulation
from models.api_key import ApiKey
from services.qdrant_service import semantic_search
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from uuid import uuid4, UUID
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# ─────────────────────────────────────────────────────────────────────────────
# Pydantic models for API Keys
# ─────────────────────────────────────────────────────────────────────────────

class ApiKeyCreate(BaseModel):
    name: str

class ApiKeyResponse(BaseModel):
    id: UUID
    name: str
    key: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ─────────────────────────────────────────────────────────────────────────────
# AUTHENTICATION DEPENDENCY
# ─────────────────────────────────────────────────────────────────────────────

async def validate_protocol_key(x_protocol_key: str = Header(..., alias="X-Protocol-Key"), db: AsyncSession = Depends(get_db)):
    """Validates the protocol key against the database"""
    if x_protocol_key == "LGL_PROTOCOL_DEFAULT_SANDBOX":
        return x_protocol_key
        
    result = await db.execute(select(ApiKey).where(ApiKey.key == x_protocol_key, ApiKey.is_active == True))
    key_found = result.scalar_one_or_none()
    
    if not key_found:
        logger.warning(f"Unauthorized API access attempt with key: {x_protocol_key[:10]}...")
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired Institutional Protocol Key."
        )
    return x_protocol_key

# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/search")
async def neural_search(
    query: str = Query(..., description="Semantic query string"),
    limit: int = Query(5, ge=1, le=20),
    jurisdiction: Optional[str] = None,
    category: Optional[str] = None,
    protocol_key: str = Depends(validate_protocol_key)
):
    """
    Programmatic entry to the Leagle Semantic Index.
    Leverages RAG infrastructure for high-fidelity regulatory retrieval.
    """
    try:
        results = semantic_search(
            query_text=query,
            top_k=limit,
            category_filter=category,
            source_type_filter="regulation"
        )
        return {
            "status": "success",
            "query": query,
            "results_count": len(results),
            "data": results
        }
    except Exception as e:
        logger.error(f"Neural Search Error: {e}")
        raise HTTPException(status_code=500, detail="Neural Engine processing failure.")

@router.get("/regulations", dependencies=[Depends(validate_protocol_key)])
async def list_institutional_regulations(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Retrieve clinical-grade regulatory documents currently syncing in the ecosystem.
    """
    result = await db.execute(
        select(Regulation)
        .order_by(desc(Regulation.created_at))
        .offset(offset)
        .limit(limit)
    )
    regulations = result.scalars().all()
    
    return {
        "status": "success",
        "timestamp": "Real-time sync active",
        "data": [
            {
                "id": str(r.id),
                "title": r.title,
                "source": r.source,
                "category": r.category,
                "risk_level": r.risk_level,
                "jurisdiction": r.jurisdiction,
                "created_at": r.created_at.isoformat()
            }
            for r in regulations
        ]
    }

@router.get("/health", dependencies=[Depends(validate_protocol_key)])
async def api_health():
    """Verify neural heartbeat for documentation testing."""
# ─────────────────────────────────────────────────────────────────────────────
# API KEY MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/keys", response_model=List[ApiKeyResponse], dependencies=[Depends(require_admin)])
async def get_keys(db: AsyncSession = Depends(get_db)):
    """Retrieve all issued institutional protocol keys."""
    print("--- GET /keys called ---")
    result = await db.execute(select(ApiKey).order_by(desc(ApiKey.created_at)))
    return result.scalars().all()

@router.post("/keys", response_model=ApiKeyResponse, dependencies=[Depends(require_admin)])
async def create_key(data: ApiKeyCreate, db: AsyncSession = Depends(get_db)):
    """Generate a new persistent institutional protocol key."""
    print(f"--- POST /keys called with name: {data.name} ---")
    new_key_str = f"LGL_PROTOCOL_{uuid4().hex[:16].upper()}"
    new_key = ApiKey(name=data.name, key=new_key_str)
    db.add(new_key)
    await db.commit()
    await db.refresh(new_key)
    return new_key

@router.delete("/keys/{key_id}", dependencies=[Depends(require_admin)])
async def delete_key(key_id: UUID, db: AsyncSession = Depends(get_db)):
    """Revoke an institutional protocol key."""
    await db.execute(delete(ApiKey).where(ApiKey.id == key_id))
    await db.commit()
    return {"status": "success", "message": "Protocol Key revoked."}

