import httpx
import logging
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from services.ingestion import ingest_regulation
from services.alert_engine import run_impact_analysis

logger = logging.getLogger(__name__)

from core.utils import get_random_user_agent

FEDERAL_REGISTER_API_URL = "https://www.federalregister.gov/api/v1/documents.json"

async def sync_us_regulations(db: AsyncSession, limit: int = 10):
    """
    Fetches the latest US Federal Register documents (Rules and Proposed Rules)
    and ingests them into Leagle.
    """
    logger.info(f"📊 Syncing US Regulations from Federal Register API")
    
    params = {
        "conditions[type][]": ["RULE", "PROPOSED_RULE"],
        "per_page": limit,
        "order": "newest"
    }
    
    headers = {"User-Agent": get_random_user_agent()}
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        try:
            response = await client.get(FEDERAL_REGISTER_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.error(f"❌ Failed to fetch US regulations: {e}")
            return 0

        results = data.get("results", [])
        print(f"📡 Found {len(results)} entries in Federal Register.")
        
        count = 0
        for doc in results:
            title = doc.get("title", "Unknown US Regulation")
            text = doc.get("abstract") or doc.get("body") or title
            source_url = doc.get("html_url")
            publication_date_str = doc.get("publication_date")
            publication_date = None
            if publication_date_str:
                try:
                    publication_date = datetime.strptime(publication_date_str, "%Y-%m-%d").date()
                except Exception:
                    pass

            agency_names = [a.get("name") for a in doc.get("agencies", [])]
            
            # Determine category based on agencies or title
            category = "compliance"
            agencies_str = " ".join(agency_names).lower()
            if "environmental" in agencies_str or "epa" in agencies_str:
                category = "environmental"
            elif "securities" in agencies_str or "sec" in agencies_str or "finance" in agencies_str:
                category = "financial"
            elif "health" in agencies_str or "fda" in agencies_str:
                category = "healthcare"
            elif "privacy" in title.lower() or "data" in title.lower():
                category = "data_privacy"

            print(f"📥 Syncing US: {title[:60]}... ({category})")
            
            try:
                regulation = await ingest_regulation(
                    db=db,
                    title=title,
                    text=f"{title}\n\n{text}",
                    source=f"Federal Register ({', '.join(agency_names)})",
                    category=category,
                    jurisdiction="United States (Federal)",
                    effective_date=publication_date
                )
                
                # Run impact analysis
                await run_impact_analysis(db, regulation)
                count += 1
            except Exception as e:
                logger.error(f"❌ Error ingesting US regulation: {e}")

    return count

if __name__ == "__main__":
    import asyncio
    from core.database import engine
    from sqlalchemy.orm import sessionmaker

    async def test():
        async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as db:
            await sync_us_regulations(db, limit=5)

    asyncio.run(test())
