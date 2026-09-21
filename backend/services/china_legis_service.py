import httpx
import logging
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession
from services.ingestion import ingest_regulation
from services.alert_engine import run_impact_analysis
from core.utils import get_random_user_agent

logger = logging.getLogger(__name__)

# State Council Policies portal (English) - Official PRC Statutory Feed
CHINA_STATE_COUNCIL_URL = "https://english.www.gov.cn/policies/latest"
CHINA_NEWS_EN_RSS = "https://news.google.com/rss/search?q=China+regulation+SAMR+PIPL+CSRC+PBOC+law&hl=en-CN&gl=CN&ceid=CN:en"

async def sync_china_regulations(db: AsyncSession, limit: int = 10) -> int:
    """Coordinates Chinese regulatory sync from official State Council portal and news alerts."""
    count = 0
    count += await _sync_china_state_council(db, limit)
    count += await _sync_china_news(db, limit // 2)
    return count

async def _sync_china_state_council(db: AsyncSession, limit: int = 10) -> int:
    """Scrapes official PRC policies from the State Council English portal."""
    logger.info("🇨🇳 Syncing China: State Council Official Portal")
    headers = {"User-Agent": get_random_user_agent()}

    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(CHINA_STATE_COUNCIL_URL)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
        except Exception as e:
            logger.error(f"❌ China State Council Portal Failure: {e}")
            return 0

        # Official policy list items
        # The portal uses a list of items within the policy section
        items = soup.select(".list-item, .list li, .latest-policies li")
        if not items:
            # Fallback to general link search
            items = [a for a in soup.find_all("a", href=True) if "/latest/" in a.get("href")]

        print(f"📡 Found {len(items)} items in China State Council portal.")
        count = 0
        unique_titles = set()
        
        for item in items:
            if count >= limit: break
            try:
                title = item.get_text().strip()
                link = item.get("href", "") if hasattr(item, "get") else ""
                
                if not title or len(title) < 10 or title in unique_titles: continue
                unique_titles.add(title)
                
                if not link.startswith("http"):
                    link = f"https://english.www.gov.cn{link}"

                category = "compliance"
                lower = title.lower()
                if any(x in lower for x in ["data", "privacy", "information", "pipl"]):
                    category = "data_privacy"
                elif any(x in lower for x in ["financial", "banking", "monetary", "csrc", "pboc"]):
                    category = "financial"
                elif any(x in lower for x in ["environment", "carbon", "climate"]):
                    category = "environmental"

                print(f"📥 Syncing China (Official): {title[:60]}... ({category})")
                regulation = await ingest_regulation(
                    db=db,
                    title=title,
                    text=f"Official Policy from the State Council of the People's Republic of China.\nSource URL: {link}",
                    source="State Council of China (Official)",
                    category=category,
                    jurisdiction="China",
                )
                await run_impact_analysis(db, regulation)
                count += 1
            except Exception as e:
                logger.debug(f"Skipping noise item in China sync: {e}")
        return count

async def _sync_china_news(db: AsyncSession, limit: int = 5) -> int:
    """Captures real-time Chinese regulatory news alerts (English)."""
    logger.info("🇨🇳 Syncing China: Google News Alerts (EN)")
    headers = {"User-Agent": get_random_user_agent()}
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(CHINA_NEWS_EN_RSS)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "xml")
        except Exception as e:
            logger.error(f"❌ China News Sync Failure: {e}")
            return 0

        items = soup.find_all("item")
        count = 0
        for item in items[:limit]:
            title = item.find("title").text if item.find("title") else "Unknown Chinese Regulatory Alert"
            link = item.find("link").text if item.find("link") else ""
            try:
                regulation = await ingest_regulation(
                    db=db,
                    title=title,
                    text=f"Regulatory Intelligence Alert (China).\nFull coverage: {link}",
                    source="China Regulatory News Alerts",
                    category="compliance",
                    jurisdiction="China",
                )
                await run_impact_analysis(db, regulation)
                count += 1
            except Exception as e:
                logger.error(f"❌ China News Ingest Error: {e}")
        return count
