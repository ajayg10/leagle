import httpx
import logging
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession
from services.ingestion import ingest_regulation
from services.alert_engine import run_impact_analysis
from core.utils import get_random_user_agent

logger = logging.getLogger(__name__)

# South Korea: Korea Legislation Research Institute (KLRI) and news
KOREA_NEWS_RSS = "https://news.google.com/rss/search?q=South+Korea+FSC+FSS+regulation+law+PIPA+legislation&hl=en-KR&gl=KR&ceid=KR:en"
# KLRI has an open legislation search API
KOREA_KLRI_RSS = "https://www.law.go.kr/LSW/nwRssListR.do?menuId=5&subMenu=5"

async def sync_southkorea_regulations(db: AsyncSession, limit: int = 10) -> int:
    """Coordinates South Korean regulatory sync from KLRI and news alerts."""
    count = 0
    count += await _sync_korea_klri(db, limit)
    count += await _sync_korea_news(db, limit // 2)
    return count

async def _sync_korea_klri(db: AsyncSession, limit: int = 10) -> int:
    """Fetches South Korean legislation from the KLRI RSS feed."""
    logger.info("🇰🇷 Syncing South Korea: KLRI RSS")
    headers = {"User-Agent": get_random_user_agent()}

    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(KOREA_KLRI_RSS)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "xml")
        except Exception as e:
            logger.error(f"❌ South Korea KLRI RSS Failure: {e}")
            return 0

        items = soup.find_all("item")
        print(f"📡 Found {len(items)} items in South Korea KLRI RSS.")
        count = 0
        for item in items[:limit]:
            title = item.find("title").text if item.find("title") else "Unknown South Korean Regulation"
            link = item.find("link").text if item.find("link") else ""
            description = item.find("description").text if item.find("description") else title

            category = "compliance"
            lower = (title + description).lower()
            if "개인정보" in title or "pipa" in lower or "personal information" in lower or "privacy" in lower:
                category = "data_privacy"
            elif "금융" in title or "fsc" in lower or "fss" in lower or "financial" in lower or "banking" in lower:
                category = "financial"
            elif "환경" in title or "environment" in lower:
                category = "environmental"
            elif "보건" in title or "health" in lower or "의료" in title:
                category = "healthcare"

            print(f"📥 Syncing South Korea: {title[:60]}... ({category})")
            try:
                regulation = await ingest_regulation(
                    db=db,
                    title=title,
                    text=f"{title}\n\n{description[:1000]}\n\nSource: {link}",
                    source="Korea Legislation Research Institute (KLRI)",
                    category=category,
                    jurisdiction="South Korea",
                )
                await run_impact_analysis(db, regulation)
                count += 1
            except Exception as e:
                logger.error(f"❌ South Korea KLRI Ingest Error: {e}")
        return count

async def _sync_korea_news(db: AsyncSession, limit: int = 5) -> int:
    """Captures real-time South Korean regulatory news alerts (English)."""
    logger.info("🇰🇷 Syncing South Korea: Google News Alerts (EN)")
    headers = {"User-Agent": get_random_user_agent()}
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(KOREA_NEWS_RSS)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "xml")
        except Exception as e:
            logger.error(f"❌ South Korea News Sync Failure: {e}")
            return 0

        items = soup.find_all("item")
        count = 0
        for item in items[:limit]:
            title = item.find("title").text if item.find("title") else "Unknown South Korean Regulatory Alert"
            link = item.find("link").text if item.find("link") else ""
            try:
                regulation = await ingest_regulation(
                    db=db,
                    title=title,
                    text=f"Regulatory Intelligence Alert (South Korea).\nFull coverage: {link}",
                    source="South Korea Regulatory News Alerts",
                    category="compliance",
                    jurisdiction="South Korea",
                )
                await run_impact_analysis(db, regulation)
                count += 1
            except Exception as e:
                logger.error(f"❌ South Korea News Ingest Error: {e}")
        return count
