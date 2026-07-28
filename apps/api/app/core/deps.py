from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from app.db.session import get_db
from app.core.redis import get_redis_client

async def db_dependency() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db():
        yield session

async def redis_dependency() -> Redis:
    return await get_redis_client()
