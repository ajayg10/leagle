import httpx
import logging
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession
from services.ingestion import ingest_regulation
from services.alert_engine import run_impact_analysis
from core.utils import get_random_user_agent
from datetime import datetime

logger = logging.getLogger(__name__)

# Official Statutory Source
INDIA_CODE_BROWSE = "https://www.indiacode.nic.in/handle/123456789/1362/browse?type=dateissued&sort_by=1&order=DESC&rpp=20"
# Real-time Alert Layer
INDIA_NEWS_RSS = "https://news.google.com/rss/search?q=India+government+regulation+policy+gazette+notification&hl=en-IN&gl=IN&ceid=IN:en"

async def sync_india_regulations(db: AsyncSession, limit: int = 10):
    """
    Coordinates Indian regulatory sync from official statutory sources and real-time news.
    """
    count = 0
    # 1. Statutory Foundation (IndiaCode)
    count += await sync_indiacode(db, limit)
    
    # 2. Real-time Alert Layer (News)
    count += await sync_india_news(db, limit // 2)
    
    # 3. Open Data Catalog (Data.gov.in)
    count += await sync_datagov_india(db, limit)
    
    return count

async def sync_indiacode(db: AsyncSession, limit: int = 10):
    """
    Scrapes the official India Code repository for the latest Acts.
    """
    logger.info(f"📊 Syncing India: IndiaCode Statutory Intake")
    headers = {"User-Agent": get_random_user_agent()}
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(INDIA_CODE_BROWSE)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            
            # The browse table rows
            table = soup.find("table", class_="table")
            if not table:
                logger.warning("⚠️ IndiaCode browse table not found.")
                return 0
                
            rows = table.find_all("tr")[1:] # Skip header
            count = 0
            
            for row in rows[:limit]:
                cols = row.find_all("td")
                if len(cols) < 3: continue
                
                date_issued = cols[0].text.strip()
                act_num = cols[1].text.strip()
                title_tag = cols[2].find("a")
                if not title_tag: continue
                
                title = title_tag.text.strip()
                handle_url = f"https://www.indiacode.nic.in{title_tag.get('href')}"
                
                print(f"📥 Fetching Statutory Details: {title[:60]}...")
                
                # Fetch deeper metadata (Ministry, etc)
                ministry = "Unknown Ministry"
                try:
                    detail_resp = await client.get(handle_url)
                    if detail_resp.status_code == 200:
                        detail_soup = BeautifulSoup(detail_resp.content, "html.parser")
                        # Look for ministry in the details table or specific actdetails div
                        details_text = detail_soup.get_text()
                        if "Ministry:" in details_text:
                            # Simple split extraction for brevity
                            ministry = details_text.split("Ministry:")[1].split("\n")[0].strip()
                except Exception as e:
                    logger.warning(f"⚠️ Metadata fetch failed for {title}: {e}")

                try:
                    regulation = await ingest_regulation(
                        db=db,
                        title=f"{title} (Act {act_num})",
                        text=f"Statutory Record from IndiaCode.\nMinistry: {ministry}\nEnactment Date: {date_issued}\nSource URL: {handle_url}",
                        source="IndiaCode Statutory Repository",
                        category="compliance",
                        jurisdiction="India (Bharat)"
                    )
                    await run_impact_analysis(db, regulation)
                    count += 1
                except Exception as e:
                    logger.error(f"❌ Statutory Ingest Error: {e}")
            
            return count
        except Exception as e:
            logger.error(f"❌ IndiaCode Sync Failure: {e}")
            return 0

async def sync_india_news(db: AsyncSession, limit: int = 10):
    """
    Captures real-time news alerts as a fallback/alert layer.
    """
    logger.info(f"📊 Syncing India: Google News Alerts")
    headers = {"User-Agent": get_random_user_agent()}
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        try:
            response = await client.get(INDIA_NEWS_RSS)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "xml")
            items = soup.find_all("item")
            
            count = 0
            for item in items[:limit]:
                title = item.find("title").text if item.find("title") else "Unknown India Regulation"
                link = item.find("link").text if item.find("link") else ""
                
                try:
                    regulation = await ingest_regulation(
                        db=db,
                        title=title,
                        text=f"Regulatory Intelligence Alert.\nFull coverage: {link}",
                        source="India Regulatory Alerts",
                        category="compliance",
                        jurisdiction="India (Bharat)"
                    )
                    await run_impact_analysis(db, regulation)
                    count += 1
                except Exception as e:
                    logger.error(f"❌ News Alert Ingest Error: {e}")
            return count
        except Exception as e:
            logger.error(f"❌ India News Sync Failure: {e}")
            return 0

async def sync_datagov_india(db: AsyncSession, limit: int = 10):
    """
    Fetches the latest datasets from Data.gov.in (OGD) related to Law/Justice.
    """
    logger.info(f"📊 Syncing India: Data.gov.in OGD Catalog")
    # Using the search results RSS or a publicly accessible catalog link
    DATA_GOV_RSS = "https://www.data.gov.in/rss.xml" 
    headers = {"User-Agent": get_random_user_agent()}
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        try:
            response = await client.get(DATA_GOV_RSS)
            if response.status_code != 200:
                logger.warning(f"⚠️ Data.gov.in RSS unavailable ({response.status_code})")
                return 0
                
            soup = BeautifulSoup(response.content, "xml")
            items = soup.find_all("item")
            
            count = 0
            for item in items[:limit]:
                title = item.find("title").text if item.find("title") else "Unknown Dataset"
                link = item.find("link").text if item.find("link") else ""
                
                # Check for legislative relevance
                keywords = ["act", "law", "justice", "rule", "regulation", "gazette", "notification"]
                if not any(k in title.lower() for k in keywords):
                    continue
                    
                print(f"📥 Syncing India (OGD): {title[:60]}...")
                
                regulation = await ingest_regulation(
                    db=db,
                    title=title,
                    text=f"Dataset Catalog Entry: {link}\n\n{title}",
                    source="Data.gov.in OGD",
                    category="compliance",
                    jurisdiction="India (Bharat)"
                )
                await run_impact_analysis(db, regulation)
                count += 1
            return count
        except Exception as e:
            logger.error(f"❌ Data.gov.in Sync Failure: {e}")
            return 0
