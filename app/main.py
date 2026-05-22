from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.ops import router as ops_router
from app.core.logging import setup_logging
from app.services.scheduler.tasks import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(application: FastAPI):
    setup_logging()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="PulseWire",
    description="Backend automation platform for Telegram publishing",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(ops_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
