from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from models.impact import ImpactMapping
from models.regulation import Regulation
from models.policy import Policy
from services.rag_pipeline import analyze_impact

router = APIRouter()

@router.post("/analyze")
async def analyze_regulation_impact(
    regulation_id: str,
    policy_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Full RAG impact analysis between a regulation and a policy."""
    reg_result = await db.execute(select(Regulation).where(Regulation.id == regulation_id))
    regulation = reg_result.scalar_one_or_none()
    if not regulation:
        raise HTTPException(404, "Regulation not found")

    pol_result = await db.execute(select(Policy).where(Policy.id == policy_id))
    policy = pol_result.scalar_one_or_none()
    if not policy:
        raise HTTPException(404, "Policy not found")

    analysis = await analyze_impact(
        regulation_text=regulation.raw_text or "",
        policy_text=policy.content or "",
        regulation_title=regulation.title,
        policy_title=policy.title,
    )

    # Update the impact mapping with LLM summary
    mapping_result = await db.execute(
        select(ImpactMapping).where(
            ImpactMapping.regulation_id == regulation_id,
            ImpactMapping.policy_id == policy_id,
        )
    )
    mapping = mapping_result.scalar_one_or_none()
    if mapping:
        mapping.impact_level = analysis.get("impact_level", mapping.impact_level)
        mapping.llm_summary = analysis.get("reasoning", "")
        await db.commit()

    return analysis

@router.get("/heatmap")
async def get_risk_heatmap(db: AsyncSession = Depends(get_db)):
    """Returns data for the 2D risk heatmap: departments × categories."""
    result = await db.execute(
        select(ImpactMapping, Policy, Regulation)
        .join(Policy, ImpactMapping.policy_id == Policy.id)
        .join(Regulation, ImpactMapping.regulation_id == Regulation.id)
        .where(ImpactMapping.status == "OPEN")
    )
    rows = result.all()

    # Build heatmap: {department: {category: max_risk_level}}
    heatmap: dict[str, dict[str, int]] = {}
    level_to_score = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}

    for mapping, policy, regulation in rows:
        dept = policy.department or "Unknown"
        cat = regulation.category or "General"
        score = level_to_score.get(mapping.impact_level or "LOW", 1)
        if dept not in heatmap:
            heatmap[dept] = {}
        heatmap[dept][cat] = max(heatmap[dept].get(cat, 0), score)

    return {"heatmap": heatmap, "total_open_impacts": len(rows)}
@router.get("/details")
async def get_impact_details(dept: str, cat: str, db: AsyncSession = Depends(get_db)):
    """Returns the list of policies and regulations that form a specific heatmap cell."""
    result = await db.execute(
        select(ImpactMapping, Policy, Regulation)
        .join(Policy, ImpactMapping.policy_id == Policy.id)
        .join(Regulation, ImpactMapping.regulation_id == Regulation.id)
        .where(
            Policy.department == dept,
            Regulation.category == cat,
            ImpactMapping.status == "OPEN"
        )
    )
    rows = result.all()

    details = []
    for mapping, policy, regulation in rows:
        details.append({
            "mapping_id": str(mapping.id),
            "policy_id": str(policy.id),
            "policy_title": policy.title,
            "regulation_id": str(regulation.id),
            "regulation_title": regulation.title,
            "impact_level": mapping.impact_level,
            "summary": mapping.llm_summary or f"Semantic overlap detected between {policy.title} and {regulation.title}."
        })
    return details
