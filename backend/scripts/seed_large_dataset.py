import asyncio
import pandas as pd
import random
import os
import sys
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

# Path setup
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.database import engine
from services.ingestion import ingest_regulation
from services.alert_engine import run_impact_analysis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CSV_PATH = "/home/perseuskyogre/Projects/CodeWizards/backend/data/training/legal_text_classified_priority.csv"

async def seed_large_dataset(limit=50):
    if not os.path.exists(CSV_PATH):
        print(f"❌ CSV not found at {CSV_PATH}")
        return

    print(f"\n📂 Loading dataset from {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    
    # Take a random sample
    sample_df = df.sample(min(limit, len(df)))
    print(f"📊 Selected {len(sample_df)} random legal precedents for ingestion.\n")

    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    categories = ["data_privacy", "compliance", "financial", "security", "operations"]
    jurisdictions = ["USA", "EU", "Global", "UK", "Australia"]

    async with async_session() as db:
        for idx, row in sample_df.iterrows():
            title = str(row["case_title"])
            text = str(row["case_text"])
            
            if not text or text.lower() == "nan":
                continue
            
            # Enrich with random (but realistic looking) metadata for heatmap variety
            category = random.choice(categories)
            jurisdiction = random.choice(jurisdictions)
            source = "Legal Precedent"
            
            print(f"🔍 Ingesting: {title[:50]}... ({category})")
            
            try:
                regulation = await ingest_regulation(
                    db=db,
                    title=title,
                    text=text,
                    source=source,
                    category=category,
                    jurisdiction=jurisdiction
                )
                
                # Run impact analysis against currently seeded policies
                await run_impact_analysis(db, regulation)
                print(f"  ✅ Mapping complete.")
            except Exception as e:
                print(f"  ❌ Error: {e}")

    print("\n" + "="*50)
    print("🎉 SCALING COMPLETE: The brain is now much more comprehensive.")
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(seed_large_dataset(limit=200))
