import httpx
import logging
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession
from services.ingestion import ingest_regulation
from services.alert_engine import run_impact_analysis
from core.utils import get_random_user_agent

logger = logging.getLogger(__name__)

# German government legislation feed (Gesetze im Internet)
GERMANY_LAWS_RSS = "https://www.gesetze-im-internet.de/aktuell.rss"
# German Federal Gazette news layer
GERMANY_NEWS_RSS = "https://news.google.com/rss/search?q=Germany+Bundesgesetzblatt+Regulierung+Gesetz&hl=de&gl=DE&ceid=DE:de"
GERMANY_NEWS_EN_RSS = "https://news.google.com/rss/search?q=Germany+federal+regulation+law+BaFin&hl=en-DE&gl=DE&ceid=DE:en"

async def sync_germany_regulations(db: AsyncSession, limit: int = 10) -> int:
    """Coordinates German regulatory sync from official law feeds and news alerts."""
    count = 0
    count += await _sync_germany_laws(db, limit)
    count += await _sync_germany_news(db, limit // 2)
    return count

async def _sync_germany_laws(db: AsyncSession, limit: int = 10) -> int:
    """Fetches new German laws from Gesetze-im-Internet RSS."""
    logger.info("🇩🇪 Syncing Germany: Gesetze-im-Internet RSS")
    headers = {"User-Agent": get_random_user_agent()}

    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(GERMANY_LAWS_RSS)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "xml")
        except Exception as e:
            logger.error(f"❌ Germany Laws RSS Failure: {e}")
            return 0

        items = soup.find_all("item")
        print(f"📡 Found {len(items)} items in Germany Laws RSS.")
        count = 0
        for item in items[:limit]:
            title = item.find("title").text if item.find("title") else "Unknown German Regulation"
            link = item.find("link").text if item.find("link") else ""
            description = item.find("description").text if item.find("description") else title

            category = "compliance"
            lower = (title + description).lower()
            if "datenschutz" in lower or "dsgvo" in lower or "privacy" in lower or "data" in lower:
                category = "data_privacy"
            elif "finanz" in lower or "bankaufsicht" in lower or "bafin" in lower or "steuer" in lower:
                category = "financial"
            elif "umwelt" in lower or "klima" in lower or "environment" in lower:
                category = "environmental"
            elif "gesundheit" in lower or "health" in lower:
                category = "healthcare"

            print(f"📥 Syncing Germany: {title[:60]}... ({category})")
            try:
                regulation = await ingest_regulation(
                    db=db,
                    title=title,
                    text=f"{title}\n\n{description}\n\nSource: {link}",
                    source="Gesetze-im-Internet (Germany)",
                    category=category,
                    jurisdiction="Germany",
                )
                await run_impact_analysis(db, regulation)
                count += 1
            except Exception as e:
                logger.error(f"❌ Germany Laws Ingest Error: {e}")
        return count

async def _sync_germany_news(db: AsyncSession, limit: int = 5) -> int:
    """Captures real-time German regulatory news alerts (English)."""
    logger.info("🇩🇪 Syncing Germany: Google News Alerts (EN)")
    headers = {"User-Agent": get_random_user_agent()}
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(GERMANY_NEWS_EN_RSS)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "xml")
        except Exception as e:
            logger.error(f"❌ Germany News Sync Failure: {e}")
            return 0

        items = soup.find_all("item")
        count = 0
        for item in items[:limit]:
            title = item.find("title").text if item.find("title") else "Unknown German Regulatory Alert"
            link = item.find("link").text if item.find("link") else ""
            try:
                regulation = await ingest_regulation(
                    db=db,
                    title=title,
                    text=f"Regulatory Intelligence Alert (Germany).\nFull coverage: {link}",
                    source="Germany Regulatory News Alerts",
                    category="compliance",
                    jurisdiction="Germany",
                )
                await run_impact_analysis(db, regulation)
                count += 1
            except Exception as e:
                logger.error(f"❌ Germany News Ingest Error: {e}")
        return count
