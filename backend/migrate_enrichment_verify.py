import asyncio
from sqlalchemy import text
from core.database import engine
from core.config import settings

async def migrate():
    print(f"🔗 Connecting to: {settings.database_url}")
    try:
        async with engine.begin() as conn:
            print("��️ Applying ALTER TABLE...")
            await conn.execute(text('ALTER TABLE regulations ADD COLUMN IF NOT EXISTS penalty_description TEXT'))
            await conn.execute(text('ALTER TABLE regulations ADD COLUMN IF NOT EXISTS legal_weight SMALLINT DEFAULT 5'))
            print("✅ Changes staged.")
        print("🎉 Migration committed successfully.")
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    asyncio.run(migrate())
