import httpx
import logging
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession
from services.ingestion import ingest_regulation
from services.alert_engine import run_impact_analysis
from core.utils import get_random_user_agent

logger = logging.getLogger(__name__)

# South Africa official government documents portal
SOUTHAFRICA_GOV_DOCS_URL = "https://www.gov.za/documents"
SOUTHAFRICA_NEWS_RSS = "https://news.google.com/rss/search?q=South+Africa+regulation+law+FSCA+SARB+POPIA&hl=en-ZA&gl=ZA&ceid=ZA:en"

async def sync_southafrica_regulations(db: AsyncSession, limit: int = 10) -> int:
    """Coordinates South African regulatory sync from official gov portal and news alerts."""
    count = 0
    count += await _sync_southafrica_gov(db, limit)
    count += await _sync_southafrica_news(db, limit // 2)
    return count

async def _sync_southafrica_gov(db: AsyncSession, limit: int = 10) -> int:
    """Scrapes official South African government documents/gazettes."""
    logger.info("🇿🇦 Syncing South Africa: gov.za Official Documents")
    headers = {"User-Agent": get_random_user_agent()}

    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(SOUTHAFRICA_GOV_DOCS_URL)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
        except Exception as e:
            logger.error(f"❌ South Africa Official Portal Failure: {e}")
            return 0

        # Find document items
        items = soup.select(".views-row, article")
        if not items:
            items = soup.find_all("span", class_="field-content")

        print(f"📡 Found {len(items)} items in South Africa gov portal.")
        count = 0
        for item in items:
            if count >= limit: break
            try:
                title_tag = item.find("a") if hasattr(item, "find") else None
                if not title_tag: continue
                
                title = title_tag.get_text().strip()
                link = title_tag.get("href", "")
                
                if not title or len(title) < 5: continue
                if not link.startswith("http"):
                    link = f"https://www.gov.za{link}"

                category = "compliance"
                lower = title.lower()
                if "popia" in lower or "data" in lower or "privacy" in lower:
                    category = "data_privacy"
                elif "financial" in lower or "banking" in lower or "fsca" in lower:
                    category = "financial"

                print(f"📥 Syncing South Africa (Official): {title[:60]}... ({category})")
                regulation = await ingest_regulation(
                    db=db,
                    title=title,
                    text=f"Official South African Government Document.\nFull Source: {link}",
                    source="South African Government (Official)",
                    category=category,
                    jurisdiction="South Africa",
                )
                await run_impact_analysis(db, regulation)
                count += 1
            except Exception as e:
                logger.debug(f"Skipping noise item in SA sync: {e}")
        return count

async def _sync_southafrica_news(db: AsyncSession, limit: int = 5) -> int:
    """Captures real-time South African regulatory news alerts."""
    logger.info("🇿🇦 Syncing South Africa: Google News Alerts (EN)")
    headers = {"User-Agent": get_random_user_agent()}
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(SOUTHAFRICA_NEWS_RSS)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "xml")
        except Exception as e:
            logger.error(f"❌ South Africa News Sync Failure: {e}")
            return 0

        items = soup.find_all("item")
        count = 0
        for item in items[:limit]:
            title = item.find("title").text if item.find("title") else "Unknown South African Alert"
            link = item.find("link").text if item.find("link") else ""
            try:
                regulation = await ingest_regulation(
                    db=db,
                    title=title,
                    text=f"Regulatory Intelligence Alert (South Africa).\nFull coverage: {link}",
                    source="South Africa Regulatory News Alerts",
                    category="compliance",
                    jurisdiction="South Africa",
                )
                await run_impact_analysis(db, regulation)
                count += 1
            except Exception as e:
                logger.error(f"❌ South Africa News Ingest Error: {e}")
        return count
