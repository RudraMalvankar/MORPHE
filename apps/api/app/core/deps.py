from typing import AsyncGenerator

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import get_redis_client
from app.db.session import get_db


async def db_dependency() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db():
        yield session

async def redis_dependency() -> Redis:
    return await get_redis_client()
