import datetime
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import db_dependency
from app.core.events import (
    TokenRefreshedEvent,
    UserLoggedInEvent,
    UserLoggedOutEvent,
    domain_event_bus,
)
from app.db.models import User
from app.modules.auth.deps import (
    RoleChecker,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
)
from app.modules.auth.repository import RefreshTokenRepository, UserRepository, verify_password
from app.modules.auth.schemas import (
    ChangePassword,
    ProfileUpdate,
    RoleAssignment,
    Token,
    UserRegister,
    UserResponse,
)

router = APIRouter()


@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister, db: AsyncSession = Depends(db_dependency)):
    user_repo = UserRepository(db)
    existing = await user_repo.get_by_email(data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists.",
        )
    user = await user_repo.create_user(
        email=data.email, password_plain=data.password, full_name=data.full_name
    )
    return user


@router.post("/auth/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(db_dependency)
):
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User account is deactivated"
        )

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    # Save refresh token in DB
    rt_repo = RefreshTokenRepository(db)
    expires_at = datetime.datetime.now(datetime.timezone.utc).replace(
        tzinfo=None
    ) + datetime.timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    await rt_repo.create_token(user.id, refresh_token, expires_at)

    # Emit Login Event
    event = UserLoggedInEvent(event_id=str(uuid.uuid4()), user_id=str(user.id), email=user.email)
    await domain_event_bus.publish(event)

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/auth/logout", status_code=status.HTTP_200_OK)
async def logout(
    token: str = Depends(decode_token),
    db: AsyncSession = Depends(db_dependency),
    authorization: Optional[str] = Header(None),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Invalid Authorization header format")

    raw_token = authorization.split(" ")[1]

    # We revoke the refresh token (if user provides it or we decode)
    payload = decode_token(raw_token)
    if payload:
        user_id = payload.get("sub")
        if user_id:
            # Emit event
            event = UserLoggedOutEvent(event_id=str(uuid.uuid4()), user_id=str(user_id))
            await domain_event_bus.publish(event)

    return {"detail": "Successfully logged out"}


@router.post("/auth/refresh", response_model=Token)
async def refresh(refresh_token: str, db: AsyncSession = Depends(db_dependency)):
    rt_repo = RefreshTokenRepository(db)
    db_token = await rt_repo.get_by_token(refresh_token)
    if not db_token or db_token.expires_at < datetime.datetime.now(datetime.timezone.utc).replace(
        tzinfo=None
    ):
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(db_token.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User is inactive or deleted")

    # Revoke old refresh token (Token Rotation)
    await rt_repo.revoke_token(refresh_token)

    # Generate new pair
    new_access = create_access_token(str(user.id))
    new_refresh = create_refresh_token(str(user.id))
    expires_at = datetime.datetime.now(datetime.timezone.utc).replace(
        tzinfo=None
    ) + datetime.timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    await rt_repo.create_token(user.id, new_refresh, expires_at)

    # Emit refreshed event
    event = TokenRefreshedEvent(event_id=str(uuid.uuid4()), user_id=str(user.id))
    await domain_event_bus.publish(event)

    return Token(access_token=new_access, refresh_token=new_refresh)


@router.get("/users/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/users/me", response_model=UserResponse)
async def update_me(
    data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
):
    user_repo = UserRepository(db)
    if data.email:
        existing = await user_repo.get_by_email(data.email)
        if existing and existing.id != current_user.id:
            raise HTTPException(status_code=400, detail="Email already in use")

    updated = await user_repo.update_profile(
        current_user.id, full_name=data.full_name, email=data.email
    )
    return updated


@router.patch("/users/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_dependency),
):
    if not verify_password(data.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    user_repo = UserRepository(db)
    await user_repo.update_password(current_user.id, data.new_password)
    return {"detail": "Password successfully updated"}


@router.delete("/users/me", status_code=status.HTTP_200_OK)
async def delete_me(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(db_dependency)
):
    user_repo = UserRepository(db)
    await user_repo.soft_delete(current_user.id)
    return {"detail": "Account successfully deactivated and soft deleted"}


# ==========================================
# ADMIN ENDPOINTS (PART 8)
# ==========================================

admin_checker = RoleChecker(["admin"])


@router.get("/admin/users", response_model=List[UserResponse])
async def list_users(
    db: AsyncSession = Depends(db_dependency), admin: User = Depends(admin_checker)
):
    user_repo = UserRepository(db)
    users = await user_repo.list_all()
    # Exclude soft deleted users by default in user repo or repository list
    return [u for u in users if not u.is_deleted]


@router.get("/admin/users/{user_id}", response_model=UserResponse)
async def get_user_details(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(db_dependency),
    admin: User = Depends(admin_checker),
):
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id_including_deleted(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/admin/users/{user_id}/role", response_model=UserResponse)
async def change_user_role(
    user_id: uuid.UUID,
    role_data: RoleAssignment,
    db: AsyncSession = Depends(db_dependency),
    admin: User = Depends(admin_checker),
):
    user_repo = UserRepository(db)
    updated = await user_repo.update_role(user_id, role_data.role)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated


@router.patch("/admin/users/{user_id}/reactivate", response_model=UserResponse)
async def reactivate_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(db_dependency),
    admin: User = Depends(admin_checker),
):
    user_repo = UserRepository(db)
    user = await user_repo.set_active_status(user_id, is_active=True)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
