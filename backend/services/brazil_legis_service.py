import httpx
import logging
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession
from services.ingestion import ingest_regulation
from services.alert_engine import run_impact_analysis
from core.utils import get_random_user_agent

logger = logging.getLogger(__name__)

# Brazil: Planalto (official federal law portal) and news
BRAZIL_NEWS_EN_RSS = "https://news.google.com/rss/search?q=Brazil+federal+law+regulation+LGPD+BACEN+CVM&hl=en-BR&gl=BR&ceid=BR:en"
# Brazil government Diário Oficial (DOU) RSS feed - Verified stable source
BRAZIL_DOU_RSS = "https://www.gov.br/imprensanacional/pt-br/servicos/RSS"

async def sync_brazil_regulations(db: AsyncSession, limit: int = 10) -> int:
    """Coordinates Brazilian regulatory sync from DOU and news alerts."""
    count = 0
    count += await _sync_brazil_dou(db, limit)
    count += await _sync_brazil_news(db, limit // 2)
    return count

async def _sync_brazil_dou(db: AsyncSession, limit: int = 10) -> int:
    """Fetches Brazilian federal regulations from Diário Oficial da União RSS."""
    logger.info("🇧🇷 Syncing Brazil: Diário Oficial da União RSS")
    headers = {"User-Agent": get_random_user_agent()}

    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(BRAZIL_DOU_RSS)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "xml")
        except Exception as e:
            logger.error(f"❌ Brazil DOU RSS Failure: {e}")
            return 0

        items = soup.find_all("item")
        print(f"📡 Found {len(items)} items in Brazil DOU RSS.")
        count = 0
        for item in items[:limit]:
            title = item.find("title").text if item.find("title") else "Unknown Brazilian Regulation"
            link = item.find("link").text if item.find("link") else ""
            description = item.find("description").text if item.find("description") else title

            try:
                description = BeautifulSoup(description, "html.parser").get_text()
            except Exception:
                pass

            category = "compliance"
            lower = (title + description).lower()
            if "lgpd" in lower or "dados pessoais" in lower or "privacy" in lower or "data" in lower:
                category = "data_privacy"
            elif "financ" in lower or "bacen" in lower or "cvm" in lower or "tributár" in lower:
                category = "financial"
            elif "ambiente" in lower or "climate" in lower or "environment" in lower:
                category = "environmental"
            elif "saúde" in lower or "health" in lower or "anvisa" in lower:
                category = "healthcare"

            print(f"📥 Syncing Brazil: {title[:60]}... ({category})")
            try:
                regulation = await ingest_regulation(
                    db=db,
                    title=title,
                    text=f"{title}\n\n{description[:1000]}\n\nSource: {link}",
                    source="Diário Oficial da União (Brazil)",
                    category=category,
                    jurisdiction="Brazil",
                )
                await run_impact_analysis(db, regulation)
                count += 1
            except Exception as e:
                logger.error(f"❌ Brazil DOU Ingest Error: {e}")
        return count

async def _sync_brazil_news(db: AsyncSession, limit: int = 5) -> int:
    """Captures real-time Brazilian regulatory news alerts (English)."""
    logger.info("🇧🇷 Syncing Brazil: Google News Alerts (EN)")
    headers = {"User-Agent": get_random_user_agent()}
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(BRAZIL_NEWS_EN_RSS)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "xml")
        except Exception as e:
            logger.error(f"❌ Brazil News Sync Failure: {e}")
            return 0

        items = soup.find_all("item")
        count = 0
        for item in items[:limit]:
            title = item.find("title").text if item.find("title") else "Unknown Brazilian Regulatory Alert"
            link = item.find("link").text if item.find("link") else ""
            try:
                regulation = await ingest_regulation(
                    db=db,
                    title=title,
                    text=f"Regulatory Intelligence Alert (Brazil).\nFull coverage: {link}",
                    source="Brazil Regulatory News Alerts",
                    category="compliance",
                    jurisdiction="Brazil",
                )
                await run_impact_analysis(db, regulation)
                count += 1
            except Exception as e:
                logger.error(f"❌ Brazil News Ingest Error: {e}")
        return count
