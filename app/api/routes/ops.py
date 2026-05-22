import asyncio

from fastapi import APIRouter, Header, HTTPException
from sqlalchemy import select

from app.core.config import settings
from app.core.logging import get_logger
from app.database.models.bot_log import BotLog
from app.database.session import async_session_factory
from app.services.processors.pipeline import run_pipeline

logger = get_logger(__name__)
router = APIRouter()


def _verify_api_key(x_api_key: str = Header(...)) -> None:
    """Validate the static API key from the X-API-Key header."""
    expected = settings.API_KEY.get_secret_value()
    if not expected or x_api_key != expected:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")


@router.get("/logs")
async def get_logs():
    """Return the 50 most recent BotLog entries."""
    async with async_session_factory() as session:
        stmt = select(BotLog).order_by(BotLog.created_at.desc()).limit(50)
        result = await session.execute(stmt)
        logs = result.scalars().all()

    return [
        {
            "id": log.id,
            "action": log.action,
            "status": log.status,
            "message": log.message,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]


@router.post("/trigger")
async def trigger_pipeline(x_api_key: str = Header(...)):
    """Manually trigger the content pipeline. Requires X-API-Key header."""
    _verify_api_key(x_api_key)
    logger.info("Pipeline manually triggered via /trigger endpoint")
    asyncio.create_task(run_pipeline())
    return {"status": "triggered", "message": "Pipeline execution started"}
