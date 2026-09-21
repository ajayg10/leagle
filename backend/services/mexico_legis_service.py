import httpx
import logging
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession
from services.ingestion import ingest_regulation
from services.alert_engine import run_impact_analysis
from core.utils import get_random_user_agent

logger = logging.getLogger(__name__)

# Mexico: DOF (Diario Oficial de la Federación) and news
MEXICO_DOF_RSS = "https://www.dof.gob.mx/rss/dof_rss.xml"
MEXICO_NEWS_EN_RSS = "https://news.google.com/rss/search?q=Mexico+regulation+law+CNBV+COFEPRIS+Banxico&hl=en-MX&gl=MX&ceid=MX:en"

async def sync_mexico_regulations(db: AsyncSession, limit: int = 10) -> int:
    """Coordinates Mexican regulatory sync from DOF and news alerts."""
    count = 0
    count += await _sync_mexico_dof(db, limit)
    count += await _sync_mexico_news(db, limit // 2)
    return count

async def _sync_mexico_dof(db: AsyncSession, limit: int = 10) -> int:
    """Fetches Mexican federal regulations from Diario Oficial de la Federación RSS."""
    logger.info("🇲🇽 Syncing Mexico: DOF RSS")
    headers = {"User-Agent": get_random_user_agent()}

    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(MEXICO_DOF_RSS)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "xml")
        except Exception as e:
            logger.error(f"❌ Mexico DOF RSS Failure: {e}")
            return 0

        items = soup.find_all("item")
        print(f"📡 Found {len(items)} items in Mexico DOF RSS.")
        count = 0
        for item in items[:limit]:
            title = item.find("title").text if item.find("title") else "Unknown Mexican Regulation"
            link = item.find("link").text if item.find("link") else ""
            description = item.find("description").text if item.find("description") else title

            try:
                description = BeautifulSoup(description, "html.parser").get_text()
            except Exception:
                pass

            category = "compliance"
            lower = (title + description).lower()
            if "datos personales" in lower or "privacy" in lower or "inai" in lower:
                category = "data_privacy"
            elif "financ" in lower or "cnbv" in lower or "banxico" in lower or "fiscal" in lower:
                category = "financial"
            elif "ambiente" in lower or "semarnat" in lower or "environment" in lower:
                category = "environmental"
            elif "salud" in lower or "cofepris" in lower or "health" in lower:
                category = "healthcare"

            print(f"📥 Syncing Mexico: {title[:60]}... ({category})")
            try:
                regulation = await ingest_regulation(
                    db=db,
                    title=title,
                    text=f"{title}\n\n{description[:1000]}\n\nSource: {link}",
                    source="Diario Oficial de la Federación (Mexico)",
                    category=category,
                    jurisdiction="Mexico",
                )
                await run_impact_analysis(db, regulation)
                count += 1
            except Exception as e:
                logger.error(f"❌ Mexico DOF Ingest Error: {e}")
        return count

async def _sync_mexico_news(db: AsyncSession, limit: int = 5) -> int:
    """Captures real-time Mexican regulatory news alerts (English)."""
    logger.info("🇲🇽 Syncing Mexico: Google News Alerts (EN)")
    headers = {"User-Agent": get_random_user_agent()}
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(MEXICO_NEWS_EN_RSS)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "xml")
        except Exception as e:
            logger.error(f"❌ Mexico News Sync Failure: {e}")
            return 0

        items = soup.find_all("item")
        count = 0
        for item in items[:limit]:
            title = item.find("title").text if item.find("title") else "Unknown Mexican Regulatory Alert"
            link = item.find("link").text if item.find("link") else ""
            try:
                regulation = await ingest_regulation(
                    db=db,
                    title=title,
                    text=f"Regulatory Intelligence Alert (Mexico).\nFull coverage: {link}",
                    source="Mexico Regulatory News Alerts",
                    category="compliance",
                    jurisdiction="Mexico",
                )
                await run_impact_analysis(db, regulation)
                count += 1
            except Exception as e:
                logger.error(f"❌ Mexico News Ingest Error: {e}")
        return count
