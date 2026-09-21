import io
import logging
from pypdf import PdfReader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.regulation import Regulation
from models.policy import Policy
from services.qdrant_service import embed_and_upsert, ensure_collection_exists, check_semantic_duplicate
from datetime import datetime, date

logger = logging.getLogger(__name__)

def parse_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file."""
    reader = PdfReader(io.BytesIO(file_bytes))
    text_parts = []
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text_parts.append(extracted.strip())
    return "\n\n".join(text_parts)

async def ingest_regulation(
    db: AsyncSession,
    title: str,
    text: str,
    source: str | None = None,
    category: str | None = None,
    jurisdiction: str | None = None,
    effective_date=None,
) -> Regulation | None:
    """
    Full industrial-grade ingestion pipeline:
    1. Check for exact title duplicate
    2. Check for semantic meaning duplicate (fuzzy)
    3. Extract deterministic entities (Dates, Penalties, Weight) via LLM
    4. Save to PostgreSQL + Qdrant
    """
    ensure_collection_exists()

    # Step 0: Strong Idempotency (Title check)
    existing = await db.execute(
        select(Regulation).where(Regulation.title == title, Regulation.jurisdiction == jurisdiction)
    )
    reg_existing = existing.scalar_one_or_none()
    if reg_existing:
        logger.info(f"⏭️ Skipping existing regulation (exact title): {title} ({jurisdiction})")
        return reg_existing

    # Step 0.5: Fuzzy Idempotency (Semantic check)
    semantic_dup = check_semantic_duplicate(text=text, jurisdiction=jurisdiction)
    if semantic_dup:
        logger.info(f"🧬 Semantic duplicate detected. Skipping {title} for '{semantic_dup['title']}'")
        return None

    # Step 1: Deterministic Entity Extraction
    from services.entity_extraction_service import extract_regulatory_entities
    entities = extract_regulatory_entities(text)
    
    # Enrichment
    extracted_date = entities.get("effective_date")
    if not effective_date and extracted_date:
        try:
            effective_date = date.fromisoformat(extracted_date)
        except ValueError:
            pass
            
    final_category = category or entities.get("category") or "compliance"
    penalty = entities.get("penalty_description")
    weight = entities.get("legal_weight", 5)

    # Step 2: Create Record
    try:
        regulation = Regulation(
            title=title,
            raw_text=text,
            source=source,
            category=final_category,
            jurisdiction=jurisdiction,
            effective_date=effective_date,
            penalty_description=penalty,
            legal_weight=weight
        )
        db.add(regulation)
        await db.flush()

        # Step 3: Vectorize
        metadata = {
            "regulation_id": str(regulation.id),
            "title": title,
            "source": source or "",
            "category": final_category,
            "jurisdiction": jurisdiction or "",
        }
        point_ids = embed_and_upsert(text=text, metadata=metadata, source_type="regulation")
        regulation.qdrant_ids = point_ids

        # Step 4: Risk Calibration (Weighted)
        from services.risk_scorer import score_regulation
        base_risk = score_regulation(text)
        # Intensity scaled by legal weight (Constitutional changes are prioritized)
        weighted_risk = min(100, int(base_risk * (weight / 5.0)))
        regulation.risk_level = weighted_risk

        await db.commit()
        await db.refresh(regulation)
        
        logger.info(f"🚀 Ingested: {title} | Risk: {weighted_risk} | Weight: {weight} | Penalty: {penalty is not None}")
        return regulation
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Ingestion Failed for {title}: {e}")
        return None

async def ingest_policy(
    db: AsyncSession,
    title: str,
    content: str,
    department: str | None = None,
    owner: str | None = None,
) -> Policy:
    """Ingest a company policy."""
    ensure_collection_exists()

    policy = Policy(title=title, content=content, department=department, owner=owner)
    db.add(policy)
    await db.flush()

    metadata = {
        "policy_id": str(policy.id),
        "title": title,
        "department": department or "",
    }
    point_ids = embed_and_upsert(text=content, metadata=metadata, source_type="policy")
    policy.qdrant_ids = point_ids

    await db.commit()
    await db.refresh(policy)
    return policy
