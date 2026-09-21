import asyncio
from core.database import engine
from sqlalchemy import select
from models.regulation import Regulation
from sqlalchemy.ext.asyncio import AsyncSession

async def run():
    async with AsyncSession(engine) as db:
        res = await db.execute(select(Regulation))
        regs = res.scalars().all()
        print(f"Regulations Ingested: {len(regs)}")

if __name__ == "__main__":
    asyncio.run(run())
