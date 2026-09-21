import asyncio
from core.database import engine
from sqlalchemy import select
from models.policy import Policy
from sqlalchemy.ext.asyncio import AsyncSession

async def run():
    async with AsyncSession(engine) as db:
        res = await db.execute(select(Policy))
        policies = res.scalars().all()
        print(f"Total Policies: {len(policies)}")
        for p in policies:
            print(f" - {p.department}: {p.title}")

if __name__ == "__main__":
    asyncio.run(run())
