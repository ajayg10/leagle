import asyncio
from core.database import engine
from sqlalchemy import select
from models.impact import ImpactMapping
from models.policy import Policy
from models.regulation import Regulation
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

async def check_data():
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        # Check Impact Mappings
        res = await session.execute(select(ImpactMapping))
        mappings = res.scalars().all()
        print(f"Total Impact Mappings: {len(mappings)}")
        
        # Check Policies
        res = await session.execute(select(Policy))
        policies = res.scalars().all()
        print(f"Total Policies: {len(policies)}")
        
        # Check Regulations
        res = await session.execute(select(Regulation))
        regs = res.scalars().all()
        print(f"Total Regulations: {len(regs)}")

        for m in mappings:
            print(f"Mapping: RegID={m.regulation_id}, PolID={m.policy_id}, Status={m.status}, Level={m.impact_level}")

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.getcwd())
    asyncio.run(check_data())
