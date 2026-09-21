from sqlalchemy import text
from core.database import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    with engine.connect() as conn:
        logger.info("🛠️ Running Enrichment Migration...")
        conn.execute(text('ALTER TABLE regulations ADD COLUMN IF NOT EXISTS penalty_description TEXT'))
        conn.execute(text('ALTER TABLE regulations ADD COLUMN IF NOT EXISTS legal_weight SMALLINT DEFAULT 5'))
        conn.commit()
        logger.info("✅ Enrichment Migration Complete.")

if __name__ == "__main__":
    migrate()
