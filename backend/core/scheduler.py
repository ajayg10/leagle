import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from services.sync_manager import sync_all_jurisdictions
from core.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def scheduled_sync():
    """Wrapper for the daily sync task."""
    logger.info("⏰ [Scheduler] Starting automated 24h jurisdictional sync...")
    async with AsyncSessionLocal() as db:
        try:
            results = await sync_all_jurisdictions(db, limit_per_source=20)
            logger.info(f"✅ [Scheduler] Automated sync completed. Total added: {results.get('total', 0)}")
        except Exception as e:
            logger.error(f"❌ [Scheduler] Automated sync failed: {e}")

def start_scheduler():
    """Initializes and starts the background scheduler."""
    if not scheduler.running:
        # Schedule for 00:00 UTC daily
        scheduler.add_job(
            scheduled_sync,
            CronTrigger(hour=0, minute=0, timezone="UTC"),
            id="global_regulatory_sync",
            replace_existing=True
        )
        scheduler.start()
        logger.info("🚀 Global Regulatory Scheduler started (Daily at 00:00 UTC)")

def stop_scheduler():
    """Gracefully shuts down the scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("🛑 Global Regulatory Scheduler stopped.")
