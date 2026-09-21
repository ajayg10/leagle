import asyncio
from sqlalchemy import select
from core.database import AsyncSessionLocal
from models.policy import Policy
from models.regulation import Regulation

async def inspect():
    async with AsyncSessionLocal() as db:
        p = await db.execute(select(Policy).where(Policy.title == 'Data Retention Policy'))
        pol = p.scalar_one_or_none()
        
        r = await db.execute(select(Regulation).where(Regulation.raw_text.like('%Personal Data%') | Regulation.raw_text.like('%Privacy%')))
        reg = r.scalars().first()
        
        print("\n=== POLICY: Access Control ===")
        print(pol.content if pol else 'NOT FOUND')
        
        print("\n=== REGULATION: Nuclear Safeguards ===")
        print(reg.raw_text[:2000] if reg else 'NOT FOUND')

if __name__ == "__main__":
    asyncio.run(inspect())
