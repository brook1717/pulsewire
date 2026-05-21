from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(application: FastAPI):
    setup_logging()
    # TODO: Initialize database tables
    # TODO: Start APScheduler
    yield
    # TODO: Shutdown scheduler


app = FastAPI(
    title="PulseWire",
    description="Backend automation platform for Telegram publishing",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
