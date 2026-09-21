import asyncio
from core.database import engine, Base
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

async def cleanup():
    async with AsyncSession(engine) as db:
        print("🧹 Cleaning up database for high-density re-scan...")
        await db.execute(text("TRUNCATE TABLE impact_mappings CASCADE;"))
        await db.execute(text("TRUNCATE TABLE alerts CASCADE;"))
        await db.execute(text("TRUNCATE TABLE regulations CASCADE;"))
        await db.execute(text("TRUNCATE TABLE policies CASCADE;"))
        await db.commit()
        print("✅ Database cleared.")

if __name__ == "__main__":
    asyncio.run(cleanup())
