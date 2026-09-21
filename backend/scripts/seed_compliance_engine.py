import sys
import os
import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Path setup
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.database import get_db, engine, Base
from models.regulation import Regulation
from models.policy import Policy
from services.ingestion import ingest_regulation
from services.alert_engine import run_impact_analysis
from scripts.seed_demo_data import DEMO_REGULATIONS, SAMPLE_POLICIES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_engine():
    # Setup session
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    async with async_session() as db:
        print("\n🚀 Starting Compliance Intelligence Seeder...\n")

        # 1. Seed Policies first (Impact Analysis needs them in Qdrant)
        print("Step 1: Ingesting Company Policies (Embedding to Qdrant)...")
        from services.ingestion import ingest_policy
        for p in SAMPLE_POLICIES:
            await ingest_policy(
                db=db,
                title=p["title"],
                content=p["text"],
                department=p["department"]
            )
            print(f"  ✅ Ingested Policy: {p['title']}")
        
        await db.commit()

        # 2. Ingest Regulations and trigger Auto-Impact
        print("\nStep 2: Ingesting Regulations & Generating Heatmap Data...")
        for r in DEMO_REGULATIONS:
            # This handles embedding, Qdrant upsert, and SQL storage
            regulation = await ingest_regulation(
                db=db,
                title=r["title"],
                text=r["text"],
                source=r["source"],
                category=r["category"],
                jurisdiction=r["jurisdiction"]
            )
            
            # Now trigger the Impact Engine specifically for this regulation
            print(f"  🧠 Analyzing Impact for: {r['title']}...")
            await run_impact_analysis(db, regulation)
            print(f"  ✅ Heatmap cells generated for {r['source']}")

        print("\n" + "="*50)
        print("🎉 SUCCESS: Heatmap data generated!")
        print("Refresh the dashboard to see the Glassmorphic Matrix.")
        print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(seed_engine())
