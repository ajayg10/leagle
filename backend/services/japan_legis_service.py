import httpx
import logging
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession
from services.ingestion import ingest_regulation
from services.alert_engine import run_impact_analysis
from core.utils import get_random_user_agent
from datetime import datetime

logger = logging.getLogger(__name__)

# e-Gov Japan Legal API V2 (Production Endpoints)
JAPAN_EGOV_V2_KEYWORD = "https://laws.e-gov.go.jp/api/2/keyword"
JAPAN_EGOV_V2_LAWS = "https://laws.e-gov.go.jp/api/2/laws"
JAPAN_EGOV_V2_BULK = "https://laws.e-gov.go.jp/bulkdownload"

async def sync_japan_regulations(db: AsyncSession, limit: int = 10) -> int:
    """
    Coordinates Japanese regulatory sync using e-Gov V2 JSON APIs.
    Priority: 
    1. Keyword discovery for recent ordinances
    2. Law List filtering for latest updates
    3. News Fallback
    """
    count = 0
    # 1. Official V2 Keyword Discovery
    count += await _sync_japan_v2_keyword(db, limit)
    
    # 2. V2 Law List (Fallback if search is restricted)
    if count < limit:
        count += await _sync_japan_v2_list(db, limit - count)
    
    # 3. News Fallback
    if count == 0:
        count += await _sync_japan_news(db, limit // 2)
        
    return count

async def _sync_japan_v2_keyword(db: AsyncSession, limit: int = 10) -> int:
    """Fetches Japanese law data using e-Gov V2 Keyword Search API."""
    logger.info("🇯🇵 Syncing Japan: e-Gov V2 Keyword Search")
    params = {
        "keyword": "規則", # Search for ordinances/regulations
        "limit": limit
    }
    headers = {"User-Agent": get_random_user_agent()}

    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(JAPAN_EGOV_V2_KEYWORD, params=params)
            if response.status_code != 200:
                logger.warning(f"⚠️ Japan e-Gov V2 Keyword API failed ({response.status_code})")
                return 0
            data = response.json()
        except Exception as e:
            logger.error(f"❌ Japan e-Gov V2 Keyword API Failure: {e}")
            return 0

        law_list = data.get("law_info", [])
        if not law_list:
            return 0

        count = 0
        for law in law_list:
            if count >= limit: break
            title = law.get("law_title") or "Unknown Japanese Regulation"
            law_num = law.get("law_num") or ""
            
            # Extract V2 amendment telemetry
            rev_info = law.get("revision_info", {})
            amend_type = str(rev_info.get("amendment_type", ""))
            
            status_prefix = ""
            if amend_type == "1":
                status_prefix = "[NEWLY ESTABLISHED] "
            elif amend_type == "2":
                status_prefix = "[PARTIALLY AMENDED] "
            elif amend_type == "3":
                status_prefix = "[REVISED] "
            elif amend_type == "8":
                status_prefix = "[ABOLISHED] "

            display_title = f"{status_prefix}{title}"
            
            category = "compliance"
            if any(x in title.lower() for x in ["privacy", "data", "個人情報"]):
                category = "data_privacy"
            elif any(x in title.lower() for x in ["finance", "bank", "金融"]):
                category = "financial"

            print(f"📥 Syncing Japan (V2): {display_title[:60]}... ({category})")
            try:
                regulation = await ingest_regulation(
                    db=db,
                    title=f"{display_title} (No. {law_num})",
                    text=f"Japanese Statutory Record (V2).\nAmendment Type: {amend_type}\nLaw Number: {law_num}",
                    source="Japan e-Gov Legal V2",
                    category=category,
                    jurisdiction="Japan",
                )
                await run_impact_analysis(db, regulation)
                count += 1
            except Exception as e:
                logger.error(f"❌ Japan V2 Ingest Error: {e}")
        return count

async def _sync_japan_v2_list(db: AsyncSession, limit: int = 5) -> int:
    """Fetches recently updated laws using e-Gov V2 Law List API."""
    logger.info("🇯🇵 Syncing Japan: e-Gov V2 Law List")
    # Get laws updated in the last 30 days
    today = datetime.now().strftime("%Y%m%d")
    params = {
        "updated_from": (datetime.now().replace(day=1)).strftime("%Y%m01"), # Start of month
        "limit": limit
    }
    headers = {"User-Agent": get_random_user_agent()}

    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(JAPAN_EGOV_V2_LAWS, params=params)
            if response.status_code != 200: return 0
            data = response.json()
            law_list = data.get("law_info", [])
            
            count = 0
            for law in law_list:
                if count >= limit: break
                title = law.get("law_title")
                law_num = law.get("law_num")
                regulation = await ingest_regulation(
                    db=db,
                    title=f"[UPDATE] {title}",
                    text=f"Statutory update detected for {title}.\nLaw Number: {law_num}",
                    source="Japan e-Gov Legal V2 List",
                    category="compliance",
                    jurisdiction="Japan",
                )
                await run_impact_analysis(db, regulation)
                count += 1
            return count
        except Exception:
            return 0

async def _sync_japan_news(db: AsyncSession, limit: int = 5) -> int:
    """Captures real-time Japanese regulatory news alerts (Fallback)."""
    logger.info("🇯🇵 Syncing Japan: Google News Alerts Fallback")
    JAPAN_LAWS_RSS = "https://news.google.com/rss/search?q=Japan+Ministry+regulation+ordinance+law+amendment&hl=en-JP&gl=JP&ceid=JP:en"
    headers = {"User-Agent": get_random_user_agent()}
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(JAPAN_LAWS_RSS)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "xml")
            items = soup.find_all("item")
            
            count = 0
            for item in items[:limit]:
                title = item.find("title").text if item.find("title") else "Unknown Japanese Alert"
                link = item.find("link").text if item.find("link") else ""
                regulation = await ingest_regulation(
                    db=db,
                    title=title,
                    text=f"Regulatory Intelligence Alert (Japan).\nFull coverage: {link}",
                    source="Japan Regulatory News (Fallback)",
                    category="compliance",
                    jurisdiction="Japan",
                )
                await run_impact_analysis(db, regulation)
                count += 1
            return count
        except Exception as e:
            logger.error(f"❌ Japan News Sync Failure: {e}")
            return 0
