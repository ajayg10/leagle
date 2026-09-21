import logging
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

# Original jurisdictions
from services.uk_legis_service import sync_uk_feed
from services.us_legis_service import sync_us_regulations
from services.eu_legis_service import sync_eu_regulations
from services.india_legis_service import sync_india_regulations
from services.australia_legis_service import sync_australia_regulations

# New jurisdictions
from services.canada_legis_service import sync_canada_regulations
from services.germany_legis_service import sync_germany_regulations
from services.france_legis_service import sync_france_regulations
from services.japan_legis_service import sync_japan_regulations
from services.china_legis_service import sync_china_regulations
from services.russia_legis_service import sync_russia_regulations
from services.brazil_legis_service import sync_brazil_regulations
from services.singapore_legis_service import sync_singapore_regulations
from services.southkorea_legis_service import sync_southkorea_regulations
from services.mexico_legis_service import sync_mexico_regulations
from services.southafrica_legis_service import sync_southafrica_regulations
from services.uae_legis_service import sync_uae_regulations

logger = logging.getLogger(__name__)

# Registry of all supported jurisdictions: (key, sync_fn, display_name)
JURISDICTION_REGISTRY = [
    ("uk",          sync_uk_feed,               "United Kingdom"),
    ("us",          sync_us_regulations,         "United States (Federal)"),
    ("eu",          sync_eu_regulations,         "European Union"),
    ("india",       sync_india_regulations,      "India (Bharat)"),
    ("australia",   sync_australia_regulations,  "Australia"),
    ("canada",      sync_canada_regulations,     "Canada"),
    ("germany",     sync_germany_regulations,    "Germany"),
    ("france",      sync_france_regulations,     "France"),
    ("japan",       sync_japan_regulations,      "Japan"),
    ("china",       sync_china_regulations,      "China"),
    ("russia",      sync_russia_regulations,     "Russia"),
    ("brazil",      sync_brazil_regulations,     "Brazil"),
    ("singapore",   sync_singapore_regulations,  "Singapore"),
    ("south_korea", sync_southkorea_regulations, "South Korea"),
    ("mexico",      sync_mexico_regulations,     "Mexico"),
    ("south_africa",sync_southafrica_regulations,"South Africa"),
    ("uae",         sync_uae_regulations,        "UAE"),
]

async def sync_all_jurisdictions(db: AsyncSession, limit_per_source: int = 100):
    """
    Coordinates synchronization across all supported legal jurisdictions.
    Runs each jurisdiction sequentially to avoid overwhelming the database and Qdrant.
    """
    logger.info(f"🚀 Starting Global Regulatory Sync across {len(JURISDICTION_REGISTRY)} jurisdictions")

    results = {key: 0 for key, _, _ in JURISDICTION_REGISTRY}
    results["total"] = 0

    for key, sync_fn, display_name in JURISDICTION_REGISTRY:
        try:
            results[key] = await sync_fn(db, limit=limit_per_source)
            logger.info(f"✅ {display_name} Sync Complete: {results[key]} items")
        except Exception as e:
            logger.error(f"❌ {display_name} Sync Failed: {e}")

    results["total"] = sum(v for k, v in results.items() if k != "total")
    logger.info(f"🏁 Global Sync Finished. Total items ingested: {results['total']}")

    return results


async def sync_jurisdiction(db: AsyncSession, jurisdiction: str, limit: int = 100):
    """
    Syncs a single jurisdiction by key (e.g. 'canada', 'japan').
    Returns the count of ingested items, or -1 if the jurisdiction is unknown.
    """
    registry_map = {key: (sync_fn, display_name) for key, sync_fn, display_name in JURISDICTION_REGISTRY}
    if jurisdiction not in registry_map:
        logger.error(f"❌ Unknown jurisdiction: '{jurisdiction}'. Valid keys: {list(registry_map.keys())}")
        return -1

    sync_fn, display_name = registry_map[jurisdiction]
    try:
        count = await sync_fn(db, limit=limit)
        logger.info(f"✅ {display_name} Sync Complete: {count} items")
        return count
    except Exception as e:
        logger.error(f"❌ {display_name} Sync Failed: {e}")
        return 0
