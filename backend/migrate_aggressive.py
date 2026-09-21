import asyncio
import os
from sqlalchemy import text
from core.database import engine

async def migrate():
    async with engine.begin() as conn:
        print("🚀 Executing Aggressive Jurisdictional Normalization...")
        await conn.execute(text("UPDATE regulations SET jurisdiction = 'IN' WHERE jurisdiction ILIKE 'India%' OR jurisdiction = 'IN'"))
        await conn.execute(text("UPDATE regulations SET jurisdiction = 'AU' WHERE jurisdiction ILIKE 'Australia%' OR jurisdiction = 'AU'"))
        await conn.execute(text("UPDATE regulations SET jurisdiction = 'US' WHERE jurisdiction ILIKE 'US%'"))
        await conn.execute(text("UPDATE regulations SET jurisdiction = 'UK' WHERE jurisdiction ILIKE 'UK' OR jurisdiction ILIKE 'GB' OR jurisdiction ILIKE 'United Kingdom'"))
        await conn.execute(text("UPDATE regulations SET jurisdiction = 'EU' WHERE jurisdiction ILIKE 'EU' OR jurisdiction ILIKE 'European%'"))
        res = await conn.execute(text("SELECT jurisdiction, COUNT(*) FROM regulations GROUP BY jurisdiction"))
        print("\n📊 New Portfolio Composition:")
        for row in res:
            print(f"  - {row[0]}: {row[1]}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(migrate())
