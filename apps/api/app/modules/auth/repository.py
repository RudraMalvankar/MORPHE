import datetime
import uuid
from typing import Optional

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.events import (
    PasswordChangedEvent,
    RoleChangedEvent,
    UserDeletedEvent,
    UserRegisteredEvent,
    UserUpdatedEvent,
    domain_event_bus,
)
from app.db.models import RefreshTokenDb, User
from app.db.repository import BaseRepository


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.email == email, User.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()

    async def get_by_id_including_deleted(self, user_id: uuid.UUID) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create_user(
        self, email: str, password_plain: str, full_name: str, role: str = "researcher"
    ) -> User:
        user = User(
            id=uuid.uuid4(),
            email=email,
            password_hash=hash_password(password_plain),
            full_name=full_name,
            role=role,
            is_active=True,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        # Emit UserRegisteredEvent
        event = UserRegisteredEvent(event_id=str(uuid.uuid4()), user_id=str(user.id), email=email)
        await domain_event_bus.publish(event)
        return user

    async def update_profile(
        self, user_id: uuid.UUID, full_name: Optional[str] = None, email: Optional[str] = None
    ) -> Optional[User]:
        user = await self.get_by_id(user_id)
        if not user:
            return None
        if full_name is not None:
            user.full_name = full_name
        if email is not None:
            user.email = email
        await self.db.commit()
        await self.db.refresh(user)

        event = UserUpdatedEvent(event_id=str(uuid.uuid4()), user_id=str(user.id))
        await domain_event_bus.publish(event)
        return user

    async def update_password(self, user_id: uuid.UUID, new_password_plain: str) -> bool:
        user = await self.get_by_id(user_id)
        if not user:
            return False
        user.password_hash = hash_password(new_password_plain)
        await self.db.commit()

        event = PasswordChangedEvent(event_id=str(uuid.uuid4()), user_id=str(user.id))
        await domain_event_bus.publish(event)
        return True

    async def update_role(self, user_id: uuid.UUID, new_role: str) -> Optional[User]:
        user = await self.get_by_id(user_id)
        if not user:
            return None
        user.role = new_role
        await self.db.commit()
        await self.db.refresh(user)

        event = RoleChangedEvent(
            event_id=str(uuid.uuid4()), user_id=str(user.id), new_role=new_role
        )
        await domain_event_bus.publish(event)
        return user

    async def set_active_status(self, user_id: uuid.UUID, is_active: bool) -> Optional[User]:
        user = await self.get_by_id_including_deleted(user_id)
        if not user:
            return None
        user.is_active = is_active
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def soft_delete(self, user_id: uuid.UUID) -> bool:
        user = await self.get_by_id(user_id)
        if not user:
            return False
        user.is_deleted = True
        user.deleted_at = datetime.datetime.utcnow()
        await self.db.commit()

        event = UserDeletedEvent(event_id=str(uuid.uuid4()), user_id=str(user_id))
        await domain_event_bus.publish(event)
        return True


class RefreshTokenRepository(BaseRepository[RefreshTokenDb]):
    def __init__(self, db: AsyncSession):
        super().__init__(RefreshTokenDb, db)

    async def get_by_token(self, token: str) -> Optional[RefreshTokenDb]:
        result = await self.db.execute(
            select(RefreshTokenDb).where(
                RefreshTokenDb.token == token, RefreshTokenDb.is_revoked.is_(False)
            )
        )
        return result.scalar_one_or_none()

    async def create_token(
        self, user_id: uuid.UUID, token: str, expires_at: datetime.datetime
    ) -> RefreshTokenDb:
        rt = RefreshTokenDb(
            id=uuid.uuid4(), user_id=user_id, token=token, expires_at=expires_at, is_revoked=False
        )
        self.db.add(rt)
        await self.db.commit()
        await self.db.refresh(rt)
        return rt

    async def revoke_token(self, token: str) -> bool:
        rt = await self.get_by_token(token)
        if rt:
            rt.is_revoked = True
            await self.db.commit()
            return True
        return False
