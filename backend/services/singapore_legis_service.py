import httpx
import logging
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession
from services.ingestion import ingest_regulation
from services.alert_engine import run_impact_analysis
from core.utils import get_random_user_agent

logger = logging.getLogger(__name__)

# Singapore: Singapore Statutes Online (SSL) and MAS regulatory feed
SINGAPORE_NEWS_RSS = "https://news.google.com/rss/search?q=Singapore+MAS+regulation+law+PDPA+compliance&hl=en-SG&gl=SG&ceid=SG:en"
# Singapore Statutes Online gazette feed - New verified endpoint
SINGAPORE_GAZETTE_RSS = "https://sso.agc.gov.sg/What's-New/New-Legislation/RSS"

async def sync_singapore_regulations(db: AsyncSession, limit: int = 10) -> int:
    """Coordinates Singaporean regulatory sync from SSO and news alerts."""
    count = 0
    count += await _sync_singapore_gazette(db, limit)
    count += await _sync_singapore_news(db, limit // 2)
    return count

async def _sync_singapore_gazette(db: AsyncSession, limit: int = 10) -> int:
    """Fetches Singapore statutes from the SSO RSS/Gazette feed."""
    logger.info("🇸🇬 Syncing Singapore: Statutes Online RSS")
    # Using hardened browser-like headers to bypass Cloudflare 467 blocks
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(SINGAPORE_GAZETTE_RSS)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "xml")
        except Exception as e:
            logger.error(f"❌ Singapore SSO RSS Failure: {e}")
            return 0

        items = soup.find_all("item")
        print(f"📡 Found {len(items)} items in Singapore SSO RSS.")
        count = 0
        for item in items[:limit]:
            title = item.find("title").text if item.find("title") else "Unknown Singapore Regulation"
            link = item.find("link").text if item.find("link") else ""
            description = item.find("description").text if item.find("description") else title

            category = "compliance"
            lower = (title + description).lower()
            if "pdpa" in lower or "personal data" in lower or "privacy" in lower:
                category = "data_privacy"
            elif "mas" in lower or "financial" in lower or "banking" in lower or "securities" in lower:
                category = "financial"
            elif "environment" in lower or "nea" in lower:
                category = "environmental"
            elif "health" in lower or "moh" in lower or "hsa" in lower:
                category = "healthcare"
            elif "cybersecurity" in lower or "csa" in lower:
                category = "security"

            print(f"📥 Syncing Singapore: {title[:60]}... ({category})")
            try:
                regulation = await ingest_regulation(
                    db=db,
                    title=title,
                    text=f"{title}\n\n{description[:1000]}\n\nSource: {link}",
                    source="Singapore Statutes Online",
                    category=category,
                    jurisdiction="Singapore",
                )
                await run_impact_analysis(db, regulation)
                count += 1
            except Exception as e:
                logger.error(f"❌ Singapore SSO Ingest Error: {e}")
        return count

async def _sync_singapore_news(db: AsyncSession, limit: int = 5) -> int:
    """Captures real-time Singaporean regulatory news alerts."""
    logger.info("🇸🇬 Syncing Singapore: Google News Alerts")
    headers = {"User-Agent": get_random_user_agent()}
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(SINGAPORE_NEWS_RSS)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "xml")
        except Exception as e:
            logger.error(f"❌ Singapore News Sync Failure: {e}")
            return 0

        items = soup.find_all("item")
        count = 0
        for item in items[:limit]:
            title = item.find("title").text if item.find("title") else "Unknown Singapore Regulatory Alert"
            link = item.find("link").text if item.find("link") else ""
            try:
                regulation = await ingest_regulation(
                    db=db,
                    title=title,
                    text=f"Regulatory Intelligence Alert (Singapore).\nFull coverage: {link}",
                    source="Singapore Regulatory News Alerts",
                    category="compliance",
                    jurisdiction="Singapore",
                )
                await run_impact_analysis(db, regulation)
                count += 1
            except Exception as e:
                logger.error(f"❌ Singapore News Ingest Error: {e}")
        return count
