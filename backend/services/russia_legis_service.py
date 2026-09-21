import httpx
import logging
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession
from services.ingestion import ingest_regulation
from services.alert_engine import run_impact_analysis
from core.utils import get_random_user_agent

logger = logging.getLogger(__name__)

# Russia: Official Federal Statutory Feed (Hot Documents)
# Migrated from legacy Garant RSS to verified HotLaw endpoints
RUSSIA_GARANT_RSS = "https://rss.garant.ru/hotlaw/federal/"
RUSSIA_NEWS_EN_RSS = "https://news.google.com/rss/search?q=Russia+federal+law+regulation+decree+Kremlin&hl=en-RU&gl=RU&ceid=RU:en"

async def sync_russia_regulations(db: AsyncSession, limit: int = 10) -> int:
    """Coordinates Russian regulatory sync from Garant HotDocs and news alerts."""
    count = 0
    count += await _sync_russia_garant(db, limit)
    count += await _sync_russia_news(db, limit // 2)
    return count

async def _sync_russia_garant(db: AsyncSession, limit: int = 10) -> int:
    """Fetches Russian federal regulations from Garant HotLaw RSS."""
    logger.info("🇷🇺 Syncing Russia: Garant.ru HotLaw RSS")
    headers = {"User-Agent": get_random_user_agent()}

    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(RUSSIA_GARANT_RSS)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "xml")
        except Exception as e:
            logger.error(f"❌ Russia Garant HotLaw RSS Failure: {e}")
            return 0

        items = soup.find_all("item")
        print(f"📡 Found {len(items)} items in Russia Garant HotLaw RSS.")
        count = 0
        for item in items[:limit]:
            title_tag = item.find("title")
            title = title_tag.text if title_tag else "Unknown Russian Regulation"
            link_tag = item.find("link")
            link = link_tag.text if link_tag else ""
            desc_tag = item.find("description")
            description = desc_tag.text if desc_tag else title

            try:
                description = BeautifulSoup(description, "html.parser").get_text()
            except Exception:
                pass

            category = "compliance"
            lower = (title + description).lower()
            if any(x in lower for x in ["personal data", "privacy", "данных"]):
                category = "data_privacy"
            elif any(x in lower for x in ["financial", "central bank", "финансов"]):
                category = "financial"

            print(f"📥 Syncing Russia (HotDocs): {title[:60]}... ({category})")
            try:
                regulation = await ingest_regulation(
                    db=db,
                    title=title,
                    text=f"{title}\n\n{description[:1000]}\n\nSource: {link}",
                    source="Garant HotDocs (Russia Official)",
                    category=category,
                    jurisdiction="Russia",
                )
                await run_impact_analysis(db, regulation)
                count += 1
            except Exception as e:
                logger.error(f"❌ Russia Garant Ingest Error: {e}")
        return count

async def _sync_russia_news(db: AsyncSession, limit: int = 5) -> int:
    """Captures real-time Russian regulatory news alerts (English)."""
    logger.info("🇷🇺 Syncing Russia: Google News Alerts (EN)")
    headers = {"User-Agent": get_random_user_agent()}
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(RUSSIA_NEWS_EN_RSS)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "xml")
        except Exception as e:
            logger.error(f"❌ Russia News Sync Failure: {e}")
            return 0

        items = soup.find_all("item")
        count = 0
        for item in items[:limit]:
            title_tag = item.find("title")
            title = title_tag.text if title_tag else "Unknown Russian Alert"
            link_tag = item.find("link")
            link = link_tag.text if link_tag else ""
            try:
                regulation = await ingest_regulation(
                    db=db,
                    title=title,
                    text=f"Regulatory Intelligence Alert (Russia).\nFull coverage: {link}",
                    source="Russia Regulatory News Alerts",
                    category="compliance",
                    jurisdiction="Russia",
                )
                await run_impact_analysis(db, regulation)
                count += 1
            except Exception as e:
                logger.error(f"❌ Russia News Ingest Error: {e}")
        return count
