from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from core.database import get_db
from core.auth import require_admin
from models.regulation import Regulation
from services.ingestion import ingest_regulation, parse_pdf
from services.alert_engine import run_impact_analysis
from services.intel_service import RegulationIntelligenceService
from pydantic import BaseModel
from typing import Optional
from datetime import date

router = APIRouter()

from sqlalchemy import func

@router.get("/jurisdictions")
async def get_available_jurisdictions(db: AsyncSession = Depends(get_db)):
    """Returns a list of all jurisdictions with record counts."""
    result = await db.execute(
        select(Regulation.jurisdiction, func.count(Regulation.id))
        .group_by(Regulation.jurisdiction)
    )
    data = result.all()
    return [{"id": j, "count": c} for j, c in data if j]

class RegulationCreate(BaseModel):
    title: str
    text: str
    source: Optional[str] = None
    category: Optional[str] = None
    jurisdiction: Optional[str] = None
    effective_date: Optional[date] = None

class RegulationResponse(BaseModel):
    id: str
    title: str
    source: Optional[str]
    category: Optional[str]
    risk_level: int
    created_at: str

    class Config:
        from_attributes = True

@router.post("/ingest", status_code=201, dependencies=[Depends(require_admin)])
async def ingest_regulation_text(
    payload: RegulationCreate,
    db: AsyncSession = Depends(get_db),
):
    """Ingest regulation from raw text → embed → Qdrant → impact analysis."""
    regulation = await ingest_regulation(
        db=db,
        title=payload.title,
        text=payload.text,
        source=payload.source,
        category=payload.category,
        jurisdiction=payload.jurisdiction,
        effective_date=payload.effective_date,
    )
    # Trigger impact analysis in background (simplified: run synchronously for demo)
    await run_impact_analysis(db, regulation)

    return {"id": str(regulation.id), "title": regulation.title, "risk_level": regulation.risk_level}

@router.post("/upload-pdf", status_code=201, dependencies=[Depends(require_admin)])
async def upload_regulation_pdf(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """Upload a regulation PDF → parse → ingest."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted")

    file_bytes = await file.read()
    text = parse_pdf(file_bytes)

    if not text.strip():
        raise HTTPException(422, "Could not extract text from PDF")

    regulation = await ingest_regulation(db=db, title=title, text=text, category=category)
    await run_impact_analysis(db, regulation)

    return {"id": str(regulation.id), "title": regulation.title, "chunks_extracted": len(text.split())}

@router.get("/")
async def list_regulations(
    jurisdiction: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Regulation)
    if jurisdiction:
        query = query.where(Regulation.jurisdiction.ilike(f"%{jurisdiction}%"))
    
    result = await db.execute(
        query.order_by(desc(Regulation.created_at)).limit(500)
    )
    regulations = result.scalars().all()
    return [
        {
            "id": str(r.id), "title": r.title, "source": r.source,
            "category": r.category, "jurisdiction": r.jurisdiction,
            "risk_level": r.risk_level,
            "created_at": r.created_at.isoformat(),
        }
        for r in regulations
    ]

@router.get("/{regulation_id}")
async def get_regulation(regulation_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Regulation).where(Regulation.id == regulation_id))
    regulation = result.scalar_one_or_none()
    if not regulation:
        raise HTTPException(status_code=404, detail="Regulation not found")
    return regulation

@router.get("/{regulation_id}/intel")
async def get_regulation_intel(regulation_id: str, db: AsyncSession = Depends(get_db)):
    """Provides AI-powered intelligence for a regulation."""
    result = await db.execute(select(Regulation).where(Regulation.id == regulation_id))
    regulation = result.scalar_one_or_none()
    if not regulation:
        raise HTTPException(status_code=404, detail="Regulation not found")
    
    intel = await RegulationIntelligenceService.get_regulation_intel(
        title=regulation.title,
        text=regulation.raw_text or regulation.title,
        jurisdiction=regulation.jurisdiction or "Global"
    )
    return intel

@router.get("/{regulation_id}/similar")
async def get_similar_regulations(regulation_id: str, top_k: int = 5, db: AsyncSession = Depends(get_db)):
    """Find top-K semantically similar regulations using Qdrant."""
    result = await db.execute(select(Regulation).where(Regulation.id == regulation_id))
    regulation = result.scalar_one_or_none()
    if not regulation:
        raise HTTPException(404, "Regulation not found")

    from services.qdrant_service import semantic_search
    similar = semantic_search(
        query_text=regulation.raw_text[:500],
        top_k=top_k + 1,
        source_type_filter="regulation",
    )
    # Exclude self
    filtered = [s for s in similar if str(s.get("regulation_id")) != str(regulation_id)][:top_k]
    return filtered
