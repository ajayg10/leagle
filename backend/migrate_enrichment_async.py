import asyncio
from sqlalchemy import text
from core.database import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def migrate():
    async with engine.begin() as conn:
        logger.info("🛠️ Running Enrichment Migration (Async)...")
        await conn.execute(text('ALTER TABLE regulations ADD COLUMN IF NOT EXISTS penalty_description TEXT'))
        await conn.execute(text('ALTER TABLE regulations ADD COLUMN IF NOT EXISTS legal_weight SMALLINT DEFAULT 5'))
        logger.info("✅ Enrichment Migration Complete.")

if __name__ == "__main__":
    asyncio.run(migrate())
