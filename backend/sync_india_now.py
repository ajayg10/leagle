import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

# Setup path to include project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from core.database import engine
from services.india_legis_service import sync_india_regulations

async def trigger():
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as db:
        print("🚀 Executing Unified Indian Intelligence Sync...")
        count = await sync_india_regulations(db, limit=20)
        print(f"✅ Sync Complete: {count} Indian records ingested.")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(trigger())
