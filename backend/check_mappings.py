import asyncio
from core.database import engine
from sqlalchemy import select
from models.impact import ImpactMapping
from sqlalchemy.ext.asyncio import AsyncSession

async def run():
    async with AsyncSession(engine) as db:
        res = await db.execute(select(ImpactMapping))
        mappings = res.scalars().all()
        print(f"Impact Mappings: {len(mappings)}")
        
        # Check if any are HIGH
        high_res = await db.execute(select(ImpactMapping).where(ImpactMapping.impact_level == "HIGH"))
        high_mappings = high_res.scalars().all()
        print(f"HIGH IMPACT mappings: {len(high_mappings)}")

if __name__ == "__main__":
    asyncio.run(run())
