from redis.asyncio import Redis
from app.core.config import settings
from app.core.logging import logger

redis_client: Redis | None = None

async def get_redis_client() -> Redis:
    global redis_client
    if redis_client is None:
        logger.info(f"Initializing Redis client at {settings.REDIS_URL}")
        redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return redis_client

async def close_redis_client():
    global redis_client
    if redis_client is not None:
        logger.info("Closing Redis connection...")
        await redis_client.close()
        redis_client = None
