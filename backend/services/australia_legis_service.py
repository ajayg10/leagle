import feedparser
import logging
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from services.ingestion import ingest_regulation
from core.utils import get_random_user_agent

logger = logging.getLogger(__name__)

# Australian Federal Register of Legislation - New Legislative Instruments
AU_FEED_URL = "https://www.legislation.gov.au/RSS/NewLegislativeInstruments"

async def sync_australia_regulations(db: AsyncSession, limit: int = 10):
    """
    Syncs new regulations from the Australian Federal Register of Legislation (RSS).
    """
    logger.info("🇦🇺 Syncing Australia regulations...")
    
    headers = {"User-Agent": get_random_user_agent()}
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        try:
            response = await client.get(AU_FEED_URL, headers=headers)
            response.raise_for_status()
            feed = feedparser.parse(response.text)
        except Exception as e:
            logger.error(f"❌ Failed to fetch Australia feed: {e}")
            return 0

    count = 0
    for entry in feed.entries[:limit]:
        try:
            # Typical ComLaw RSS entry:
            # title: F2024L00XXX - Name of instrument
            # link: URL
            # published: Date string
            
            pub_date = None
            if hasattr(entry, 'published'):
                try:
                    # Parse RSS date: 'Tue, 22 Apr 2026 12:00:00 GMT'
                    pub_date = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %Z').date()
                except:
                    pub_date = datetime.now().date()

            regulation = await ingest_regulation(
                db=db,
                title=entry.title,
                text=entry.summary if hasattr(entry, 'summary') else entry.title,
                source=entry.link,
                category="Legislative Instrument",
                jurisdiction="AU",
                effective_date=pub_date
            )
            if regulation:
                count += 1
        except Exception as e:
            logger.error(f"❌ Error ingesting Australia entry '{entry.get('title')}': {e}")
            continue
            
    logger.info(f"✅ Australia Sync Complete: {count} items ingested")
    return count
