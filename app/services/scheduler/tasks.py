from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings
from app.core.logging import get_logger
from app.services.processors.pipeline import run_pipeline

logger = get_logger(__name__)

scheduler = AsyncIOScheduler()


def start_scheduler() -> None:
    """Configure and start the APScheduler instance."""
    scheduler.add_job(
        run_pipeline,
        trigger=IntervalTrigger(hours=settings.SCHEDULER_INTERVAL_HOURS),
        id="run_pipeline",
        name="PulseWire content pipeline",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        "Scheduler started — pipeline runs every %d hour(s)",
        settings.SCHEDULER_INTERVAL_HOURS,
    )


def stop_scheduler() -> None:
    """Gracefully shut down the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
