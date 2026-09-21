import httpx
import logging
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession
from services.ingestion import ingest_regulation
from services.alert_engine import run_impact_analysis
from core.utils import get_random_user_agent

logger = logging.getLogger(__name__)

# France: Official Statutory Feeds
# vie-publique.fr is a stable official government portal for French laws
FRANCE_LAWS_RSS = "https://www.vie-publique.fr/lois-feeds.xml"
FRANCE_NEWS_EN_RSS = "https://news.google.com/rss/search?q=France+regulation+law+RGPD+CNIL+AMF&hl=en-FR&gl=FR&ceid=FR:en"

async def sync_france_regulations(db: AsyncSession, limit: int = 10) -> int:
    """Coordinates French regulatory sync from Official Portal and news alerts."""
    count = 0
    count += await _sync_france_gov(db, limit)
    count += await _sync_france_news(db, limit // 2)
    return count

async def _sync_france_gov(db: AsyncSession, limit: int = 10) -> int:
    """Fetches French laws from the vie-publique.fr RSS feed."""
    logger.info("🇫🇷 Syncing France: Vie-publique.fr RSS")
    headers = {"User-Agent": get_random_user_agent()}

    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(FRANCE_LAWS_RSS)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "xml")
        except Exception as e:
            logger.error(f"❌ France Vie-publique RSS Failure: {e}")
            return 0

        items = soup.find_all("item")
        print(f"📡 Found {len(items)} items in France Vie-publique RSS.")
        count = 0
        for item in items[:limit]:
            title_tag = item.find("title")
            title = title_tag.text if title_tag else "Unknown French Regulation"
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
            if any(x in lower for x in ["rgpd", "données", "privacy", "data"]):
                category = "data_privacy"
            elif any(x in lower for x in ["financier", "amf", "banque", "tax"]):
                category = "financial"

            print(f"📥 Syncing France (Official): {title[:60]}... ({category})")
            try:
                regulation = await ingest_regulation(
                    db=db,
                    title=title,
                    text=f"{title}\n\n{description[:1000]}\n\nSource: {link}",
                    source="Vie-publique (France Official)",
                    category=category,
                    jurisdiction="France",
                )
                await run_impact_analysis(db, regulation)
                count += 1
            except Exception as e:
                logger.error(f"❌ France Gov Ingest Error: {e}")
        return count

async def _sync_france_news(db: AsyncSession, limit: int = 5) -> int:
    """Captures real-time French regulatory news alerts (English)."""
    logger.info("🇫🇷 Syncing France: Google News Alerts (EN)")
    headers = {"User-Agent": get_random_user_agent()}
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(FRANCE_NEWS_EN_RSS)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "xml")
        except Exception as e:
            logger.error(f"❌ France News Sync Failure: {e}")
            return 0

        items = soup.find_all("item")
        count = 0
        for item in items[:limit]:
            title_tag = item.find("title")
            title = title_tag.text if title_tag else "Unknown French Regulatory Alert"
            link_tag = item.find("link")
            link = link_tag.text if link_tag else ""
            try:
                regulation = await ingest_regulation(
                    db=db,
                    title=title,
                    text=f"Regulatory Intelligence Alert (France).\nFull coverage: {link}",
                    source="France Regulatory News Alerts",
                    category="compliance",
                    jurisdiction="France",
                )
                await run_impact_analysis(db, regulation)
                count += 1
            except Exception as e:
                logger.error(f"❌ France News Ingest Error: {e}")
        return count
