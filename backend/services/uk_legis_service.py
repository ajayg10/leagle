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

UK_FEED_URL = "https://www.legislation.gov.uk/new/data.feed"

async def sync_uk_feed(db: AsyncSession, limit: int = 10):
    """
    Fetches the latest UK legislation from the official Atom feed
    and ingests it into our compliance brain.
    """
    logger.info(f"📊 Syncing UK Legislation Feed: {UK_FEED_URL}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    async with httpx.AsyncClient(headers=headers) as client:
        try:
            response = await client.get(UK_FEED_URL)
            print(f"📡 UK Feed Response Status: {response.status_code}")
            print(f"📡 UK Feed Response Snippet: {response.text[:200]}")
            response.raise_for_status()
        except Exception as e:
            logger.error(f"❌ Failed to fetch UK feed: {e}")
            return 0

        soup = BeautifulSoup(response.content, "xml")
        # Atom namespaces can be tricky. Use a name-only search for 'entry'
        entries = soup.find_all(lambda tag: tag.name.split(':')[-1] == 'entry')
        print(f"📡 Found {len(entries)} entries in UK feed (name-agnostic).")
        
        # If still 0, try searching without the xml parser's namespace restriction
        if not entries:
            soup_html = BeautifulSoup(response.content, "html.parser")
            entries = soup_html.find_all("entry")
            print(f"📡 Fallback search found {len(entries)} entries.")
        
        count = 0
        for entry in entries[:limit]:
            title = entry.find("title").text if entry.find("title") else "Unknown UK Regulation"
            
            # Find the XML data link
            link_tag = entry.find("link", {"type": "application/xml"})
            if not link_tag:
                link_tag = entry.find("link", {"rel": "alternate"})
            
            link = link_tag.get("href") if link_tag else None
            summary = entry.find("summary").text if entry.find("summary") else ""
            
            # Determine category based on DocumentMainType or Title
            doc_type = entry.find("ukm:DocumentMainType")
            category = "compliance" # Default
            
            if doc_type:
                dt_val = doc_type.get("Value", "").lower()
                if "data" in dt_val or "privacy" in dt_val:
                    category = "data_privacy"
                elif "finance" in dt_val or "tax" in dt_val:
                    category = "financial"
                elif "security" in dt_val:
                    category = "security"
            
            # If summary is too short, try to fetch the full XML text (optional optimization)
            full_text = summary
            if link and link.endswith("/data.xml"):
                try:
                    xml_resp = await client.get(link)
                    if xml_resp.status_code == 200:
                        xml_soup = BeautifulSoup(xml_resp.content, "xml")
                        # Basic extraction of legislation text
                        text_content = xml_soup.find("Legislation")
                        if text_content:
                            full_text = text_content.get_text(separator="\n", strip=True)
                except Exception as e:
                    logger.warning(f"⚠️ Could not fetch full XML for {title}: {e}")

            print(f"📥 Syncing UK: {title[:60]}... ({category})")
            
            try:
                regulation = await ingest_regulation(
                    db=db,
                    title=title,
                    text=full_text or title,
                    source="UK Legislation API",
                    category=category,
                    jurisdiction="United Kingdom"
                )
                
                # Run impact analysis against internal policies
                await run_impact_analysis(db, regulation)
                count += 1
            except Exception as e:
                logger.error(f"❌ Error ingesting UK regulation: {e}")

    return count

if __name__ == "__main__":
    # Local test
    import asyncio
    from core.database import engine
    from sqlalchemy.orm import sessionmaker

    async def test():
        async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as db:
            await sync_uk_feed(db, limit=5)

    asyncio.run(test())
