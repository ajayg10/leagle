import httpx
import logging
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession
from services.ingestion import ingest_regulation
from services.alert_engine import run_impact_analysis
from core.utils import get_random_user_agent

logger = logging.getLogger(__name__)

# DIFC Laws & Regulations - Official Portal (UAE)
UAE_DIFC_URL = "https://www.difc.ae/business/laws-regulations/legal-database/"
UAE_DIFC_RSS = "https://www.difc.ae/business/laws-regulations/rss" 
UAE_NEWS_RSS = "https://news.google.com/rss/search?q=UAE+regulation+law+CBUAE+SCA+DIFC+ADGM&hl=en-AE&gl=AE&ceid=AE:en"

async def sync_uae_regulations(db: AsyncSession, limit: int = 10) -> int:
    """Coordinates UAE regulatory sync from DIFC portal and news alerts."""
    count = 0
    count += await _sync_uae_difc(db, limit)
    count += await _sync_uae_news(db, limit // 2)
    return count

async def _sync_uae_difc(db: AsyncSession, limit: int = 10) -> int:
    """Fetches UAE/DIFC laws from the DIFC laws & regulations portal RSS."""
    logger.info("🇦🇪 Syncing UAE: DIFC Laws & Regulations RSS")
    headers = {"User-Agent": get_random_user_agent()}

    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(UAE_DIFC_RSS)
            if response.status_code == 404:
                logger.warning("⚠️ UAE DIFC RSS returned 404, skipping to portal scraping.")
                return 0 # Scraper can be added here if needed
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "xml")
        except Exception as e:
            logger.error(f"❌ UAE DIFC RSS Failure: {e}")
            return 0

        items = soup.find_all("item")
        print(f"📡 Found {len(items)} items in UAE DIFC RSS.")
        count = 0
        for item in items[:limit]:
            title = item.find("title").text if item.find("title") else "Unknown UAE Regulation"
            link = item.find("link").text if item.find("link") else ""
            description = item.find("description").text if item.find("description") else title

            try:
                description = BeautifulSoup(description, "html.parser").get_text()
            except Exception:
                pass

            category = "compliance"
            lower = (title + description).lower()
            if any(x in lower for x in ["data protection", "privacy", "pdpl"]):
                category = "data_privacy"
            elif any(x in lower for x in ["financial", "cbuae", "sca", "adgm", "difc"]):
                category = "financial"

            print(f"📥 Syncing UAE: {title[:60]}... ({category})")
            try:
                regulation = await ingest_regulation(
                    db=db,
                    title=title,
                    text=f"{title}\n\n{description[:1000]}\n\nSource: {link}",
                    source="DIFC Laws & Regulations (UAE)",
                    category=category,
                    jurisdiction="UAE",
                )
                await run_impact_analysis(db, regulation)
                count += 1
            except Exception as e:
                logger.error(f"❌ UAE DIFC Ingest Error: {e}")
        return count

async def _sync_uae_news(db: AsyncSession, limit: int = 5) -> int:
    """Captures real-time UAE regulatory news alerts."""
    logger.info("🇦🇪 Syncing UAE: Google News Alerts (EN)")
    headers = {"User-Agent": get_random_user_agent()}
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(UAE_NEWS_RSS)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "xml")
        except Exception as e:
            logger.error(f"❌ UAE News Sync Failure: {e}")
            return 0

        items = soup.find_all("item")
        count = 0
        for item in items[:limit]:
            title_tag = item.find("title")
            title = title_tag.text if title_tag else "Unknown UAE Regulatory Alert"
            link_tag = item.find("link")
            link = link_tag.text if link_tag else ""
            try:
                regulation = await ingest_regulation(
                    db=db,
                    title=title,
                    text=f"Regulatory Intelligence Alert (UAE).\nFull coverage: {link}",
                    source="UAE Regulatory News Alerts",
                    category="compliance",
                    jurisdiction="UAE",
                )
                await run_impact_analysis(db, regulation)
                count += 1
            except Exception as e:
                logger.error(f"❌ UAE News Ingest Error: {e}")
        return count
