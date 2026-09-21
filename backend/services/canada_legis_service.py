import httpx
import logging
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession
from services.ingestion import ingest_regulation
from services.alert_engine import run_impact_analysis
from core.utils import get_random_user_agent

logger = logging.getLogger(__name__)

# Justice Laws Canada - Recent Acts RSS feed
CANADA_LAWS_RSS = "https://laws-lois.justice.gc.ca/RSS/Regulations-New.xml"
# Real-time alert layer
CANADA_NEWS_RSS = "https://news.google.com/rss/search?q=Canada+federal+regulation+legislation+gazette&hl=en-CA&gl=CA&ceid=CA:en"

async def sync_canada_regulations(db: AsyncSession, limit: int = 10) -> int:
    """Coordinates Canadian regulatory sync from Justice Laws and news alerts."""
    count = 0
    count += await _sync_canada_laws(db, limit)
    count += await _sync_canada_news(db, limit // 2)
    return count

async def _sync_canada_laws(db: AsyncSession, limit: int = 10) -> int:
    """Fetches new Canadian regulations from the Justice Laws RSS feed."""
    logger.info("🇨🇦 Syncing Canada: Justice Laws RSS")
    headers = {"User-Agent": get_random_user_agent()}

    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(CANADA_LAWS_RSS)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "xml")
        except Exception as e:
            logger.error(f"❌ Canada Laws RSS Failure: {e}")
            return 0

        items = soup.find_all("item")
        print(f"📡 Found {len(items)} items in Canada Laws RSS.")
        count = 0
        for item in items[:limit]:
            title = item.find("title").text if item.find("title") else "Unknown Canadian Regulation"
            link = item.find("link").text if item.find("link") else ""
            description = item.find("description").text if item.find("description") else title

            category = "compliance"
            lower = (title + description).lower()
            if "privacy" in lower or "data" in lower:
                category = "data_privacy"
            elif "finance" in lower or "banking" in lower or "tax" in lower:
                category = "financial"
            elif "environment" in lower or "climate" in lower:
                category = "environmental"
            elif "health" in lower:
                category = "healthcare"

            print(f"📥 Syncing Canada: {title[:60]}... ({category})")
            try:
                regulation = await ingest_regulation(
                    db=db,
                    title=title,
                    text=f"{title}\n\n{description}\n\nSource: {link}",
                    source="Justice Laws Canada RSS",
                    category=category,
                    jurisdiction="CA",
                )
                await run_impact_analysis(db, regulation)
                count += 1
            except Exception as e:
                logger.error(f"❌ Canada Laws Ingest Error: {e}")
        return count

async def _sync_canada_news(db: AsyncSession, limit: int = 5) -> int:
    """Captures real-time Canadian regulatory news alerts."""
    logger.info("🇨🇦 Syncing Canada: Google News Alerts")
    headers = {"User-Agent": get_random_user_agent()}
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(CANADA_NEWS_RSS)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "xml")
        except Exception as e:
            logger.error(f"❌ Canada News Sync Failure: {e}")
            return 0

        items = soup.find_all("item")
        count = 0
        for item in items[:limit]:
            title = item.find("title").text if item.find("title") else "Unknown Canada Regulatory Alert"
            link = item.find("link").text if item.find("link") else ""
            try:
                regulation = await ingest_regulation(
                    db=db,
                    title=title,
                    text=f"Regulatory Intelligence Alert (Canada).\nFull coverage: {link}",
                    source="Canada Regulatory News Alerts",
                    category="compliance",
                    jurisdiction="CA",
                )
                await run_impact_analysis(db, regulation)
                count += 1
            except Exception as e:
                logger.error(f"❌ Canada News Ingest Error: {e}")
        return count
