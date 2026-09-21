import asyncio
from sqlalchemy import select
from core.database import AsyncSessionLocal
from models.regulation import Regulation
from models.policy import Policy

async def check():
    async with AsyncSessionLocal() as db:
        r = await db.execute(select(Regulation.title).where(Regulation.raw_text.like('%Digital Personal Data Protection Act%')))
        title = r.scalar_one_or_none()
        print(f"DPDP_TITLE: {title}")

if __name__ == "__main__":
    asyncio.run(check())
