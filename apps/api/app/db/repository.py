from typing import Any, Generic, List, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, entity_id: Any) -> Optional[T]:
        result = await self.db.execute(
            select(self.model).where(getattr(self.model, "id") == entity_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> List[T]:
        result = await self.db.execute(select(self.model))
        return list(result.scalars().all())

    async def delete(self, entity_id: Any) -> bool:
        entity = await self.get_by_id(entity_id)
        if entity:
            await self.db.delete(entity)
            await self.db.commit()
            return True
        return False
