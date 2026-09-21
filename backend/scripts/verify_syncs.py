import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.sync_manager import sync_all_jurisdictions
from core.database import engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

async def verify():
    print("🧪 Verifying Jurisdictional Sync Services...")
    
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    async with async_session() as db:
        results = await sync_all_jurisdictions(db, limit_per_source=2)
        
        print("\n" + "="*40)
        print("SYNC VERIFICATION RESULTS")
        print("="*40)
        for jurisdiction, count in results.items():
            if jurisdiction != "total":
                print(f"📍 {jurisdiction.upper()}: {count} items ingested")
        print("-" * 40)
        print(f"🏆 TOTAL: {results['total']} items")
        print("="*40)

if __name__ == "__main__":
    asyncio.run(verify())
