import asyncio
import os
import sys

# Path setup
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from services.ingestion import ingest_regulation
from services.alert_engine import run_impact_analysis

UK_SAMPLES = [
    {
        "title": "Commission Decision (Euratom) 2020/2255 - Nuclear Cooperation Agreement",
        "text": """This decision marks a significant legal step in the post-Brexit relationship between the United Kingdom and the European Atomic Energy Community (Euratom). Adopted under Article 101 of the Euratom Treaty, it authorizes the European Commission to conclude and provisionally apply a bilateral agreement for cooperation on the safe and peaceful uses of nuclear energy. The agreement is designed to replace the framework that existed while the UK was a member of Euratom, ensuring continuity in critical areas such as nuclear safety, radioactive waste management, and the transfer of nuclear technology and materials. It also covers the provisional application of the broader Trade and Cooperation Agreement (TCA) in relation to Euratom matters.""",
        "category": "compliance",
        "jurisdiction": "UK"
    },
    {
        "title": "Commission Implementing Regulation (EU) 2020/2254 - Preferred Origin Statements",
        "text": """This Implementing Regulation was introduced to smooth the transition into the new trading arrangements established by the EU-UK Trade and Cooperation Agreement (TCA). A core feature of the TCA is the provision for zero tariffs on goods that qualify as originating in either the EU or the UK. To claim these preferential tariffs, exporters must provide a 'statement on origin,' which is often based on supporting documentation known as 'supplier’s declarations.' Recognizing that the sudden shift in trade rules on January 1, 2021, might leave many EU exporters without the necessary declarations in hand, the Commission adopted this regulation to allow for a 'transitory period.'""",
        "category": "financial",
        "jurisdiction": "UK"
    },
    {
        "title": "Council Decision (Euratom) 2020/2253 - UK-Euratom Nuclear Safeguards",
        "text": """This Council Decision represents the legislative approval from the EU Member States for the nuclear cooperation agreement with the United Kingdom. While the Commission (Decision 2020/2255) manages the administrative and technical conclusion of the agreement, the Council provides the political and legal mandate necessary for such an international treaty. The decision confirms that the negotiated agreement between the UK and Euratom meets the Community's objectives of ensuring nuclear safety, security, and the peaceful use of nuclear energy. It covers a wide range of cooperative activities, including the exchange of scientific and technical information.""",
        "category": "compliance",
        "jurisdiction": "UK"
    }
]

async def seed_uk_samples():
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as db:
        print(f"🌱 Seeding {len(UK_SAMPLES)} UK Legislation Samples...")
        for sample in UK_SAMPLES:
            try:
                reg = await ingest_regulation(
                    db=db,
                    title=sample["title"],
                    text=sample["text"],
                    source="UK Legislation Feed (Manual Sync)",
                    category=sample["category"],
                    jurisdiction=sample["jurisdiction"]
                )
                await run_impact_analysis(db, reg)
                print(f"✅ Ingested: {sample['title']}")
            except Exception as e:
                print(f"❌ Error seeding {sample['title']}: {e}")

if __name__ == "__main__":
    asyncio.run(seed_uk_samples())
