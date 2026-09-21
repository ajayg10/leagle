import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.regulation import Regulation
from models.policy import Policy
from models.impact import ImpactMapping
from models.alert import Alert
from services.qdrant_service import semantic_search
from services.risk_scorer import score_to_level
from services.websocket_service import broadcast_alert

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLDS = {
    "HIGH": 0.65,      # Lowered from 0.75 to surface more critical matches
    "MEDIUM": 0.45,    # Lowered from 0.50
    "LOW": 0.25,       # Lowered from 0.30
}

async def run_impact_analysis(
    db: AsyncSession,
    regulation: Regulation,
) -> list[ImpactMapping]:
    """
    For a newly ingested regulation:
    1. Search Qdrant for similar policy chunks (source_type=policy)
    2. Create ImpactMapping records
    3. Fire alerts for HIGH/MEDIUM impacts
    Returns list of created ImpactMapping records.
    """
    if not regulation.raw_text:
        return []

    # Search specifically in policy vectors
    similar_policies = semantic_search(
        query_text=regulation.raw_text[:1000],   # use first 1000 chars as query
        top_k=20,                               # increased from 10
        source_type_filter="policy",
        score_threshold=SIMILARITY_THRESHOLDS["LOW"],
    )

    # Deduplicate by policy_id (take the highest score per policy)
    seen_policy_ids: dict[str, dict] = {}
    for result in similar_policies:
        pid = result.get("policy_id")
        if pid and (pid not in seen_policy_ids or result["score"] > seen_policy_ids[pid]["score"]):
            seen_policy_ids[pid] = result

    mappings_created = []

    for policy_id_str, result in seen_policy_ids.items():
        similarity = result["score"]
        
        # Calculate Combined Intelligence Score (0-100)
        # We weigh content similarity (impact) and inherent regulation risk
        reg_risk = regulation.risk_level or 0
        intelligence_score = int((similarity * 70) + (reg_risk * 0.3))
        intelligence_score = max(0, min(100, intelligence_score))

        # Harmonize severity with the combined score using standard risk thresholds
        impact_level = score_to_level(intelligence_score)

        # Verify policy exists in SQL before mapping
        pol_check = await db.execute(select(Policy).where(Policy.id == policy_id_str))
        if not pol_check.scalar_one_or_none():
            logger.warning(f"⚠️ Policy {policy_id_str} in Qdrant but not in SQL. Skipping.")
            continue

        # Check if mapping already exists
        existing = await db.execute(
            select(ImpactMapping).where(
                ImpactMapping.regulation_id == regulation.id,
                ImpactMapping.policy_id == policy_id_str,
            )
        )
        if existing.scalar_one_or_none():
            continue

        mapping = ImpactMapping(
            regulation_id=regulation.id,
            policy_id=policy_id_str,
            similarity=similarity,
            impact_level=impact_level,
            status="OPEN",
        )
        db.add(mapping)
        mappings_created.append(mapping)

        # Create alert for HIGH and MEDIUM impacts
        if impact_level in ("HIGH", "MEDIUM"):
            alert = Alert(
                regulation_id=regulation.id,
                severity=impact_level,
                title=f"New Compliance Risk: {regulation.title}",
                message=(
                    f"{impact_level} impact detected: '{regulation.title}' "
                    f"matches policy profile (correlation: {similarity:.2f}). "
                    f"Intelligence Score: {intelligence_score}/100."
                ),
            )
            db.add(alert)
            
            # Broadcast real-time alert via WebSocket
            await broadcast_alert({
                "id": str(alert.id) if hasattr(alert, 'id') else "new",
                "severity": alert.severity,
                "message": alert.message,
                "regulation_title": regulation.title
            })

    await db.commit()
    logger.info(f"Created {len(mappings_created)} impact mappings for: {regulation.title}")
    return mappings_created
