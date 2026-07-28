from arq import Worker
from app.core.config import settings
from app.core.logging import logger

async def startup(ctx: dict):
    logger.info("Initializing ARQ background task worker...")

async def shutdown(ctx: dict):
    logger.info("Shutting down ARQ background worker...")

class WorkerSettings:
    functions = []
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = settings.REDIS_URL
