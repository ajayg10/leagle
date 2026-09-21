import httpx
import logging
import os
import sys
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession

# Path setup
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ingestion import ingest_regulation
from services.alert_engine import run_impact_analysis

logger = logging.getLogger(__name__)

from core.utils import get_random_user_agent

EU_RSS_URL = "https://eur-lex.europa.eu/EN/display-feed.rss?rssId=222"

async def sync_eu_regulations(db: AsyncSession, limit: int = 10):
    """
    Fetches the latest EU legislation from the EUR-Lex RSS feed.
    """
    logger.info(f"📊 Syncing EU Regulations from EUR-Lex RSS")
    
    headers = {"User-Agent": get_random_user_agent()}
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        try:
            response = await client.get(EU_RSS_URL)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "xml")
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ EU RSS HTTP Error: {e.response.status_code} - {e.response.text[:200]}")
            return 0
        except Exception as e:
            logger.error(f"❌ Failed to fetch EU RSS feed: {type(e).__name__}: {e}")
            return 0

        items = soup.find_all("item")
        print(f"📡 Found {len(items)} items in EU RSS.")
        
        count = 0
        for item in items[:limit]:
            title = item.find("title").text if item.find("title") else "Unknown EU Regulation"
            link = item.find("link").text if item.find("link") else ""
            description = item.find("description").text if item.find("description") else ""
            pub_date = item.find("pubDate").text if item.find("pubDate") else None
            
            # Basic category mapping
            category = "compliance"
            if "data" in title.lower() or "privacy" in title.lower():
                category = "data_privacy"
            elif "finance" in title.lower() or "banking" in title.lower():
                category = "financial"
            elif "environment" in title.lower() or "climate" in title.lower():
                category = "environmental"

            print(f"📥 Syncing EU: {title[:60]}... ({category})")
            
            try:
                regulation = await ingest_regulation(
                    db=db,
                    title=title,
                    text=f"{title}\n\n{description}",
                    source="EUR-Lex RSS",
                    category=category,
                    jurisdiction="European Union",
                    effective_date=None # Could parse pub_date
                )
                
                await run_impact_analysis(db, regulation)
                count += 1
            except Exception as e:
                logger.error(f"❌ Error ingesting EU regulation: {e}")

    return count

if __name__ == "__main__":
    import asyncio
    from core.database import engine
    from sqlalchemy.orm import sessionmaker

    async def test():
        async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as db:
            await sync_eu_regulations(db, limit=5)

    asyncio.run(test())
