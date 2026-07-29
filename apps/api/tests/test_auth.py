import datetime
import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.deps import db_dependency
from app.db.base import Base
from app.db.models import RefreshTokenDb
from app.main import app
from app.modules.auth.deps import create_access_token, create_refresh_token
from app.modules.auth.repository import UserRepository

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_local = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_local() as session:
        yield session
        await session.rollback()

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    async def override_db():
        yield db_session

    from httpx import ASGITransport

    app.dependency_overrides[db_dependency] = override_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_auth_registration(client, db_session):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "researcher@morphe.edu",
            "password": "secure_password_123",
            "full_name": "Dr. Newton",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "researcher@morphe.edu"
    assert data["full_name"] == "Dr. Newton"
    assert data["role"] == "researcher"
    assert "id" in data


@pytest.mark.asyncio
async def test_auth_login_success(client, db_session):
    # Setup user
    user_repo = UserRepository(db_session)
    _user = await user_repo.create_user("user@morphe.edu", "password123", "Alice")

    # Attempt login
    response = await client.post(
        "/api/v1/auth/login", data={"username": "user@morphe.edu", "password": "password123"}
    )
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_auth_login_invalid_password(client, db_session):
    user_repo = UserRepository(db_session)
    await user_repo.create_user("user@morphe.edu", "password123", "Alice")

    response = await client.post(
        "/api/v1/auth/login", data={"username": "user@morphe.edu", "password": "wrongpassword"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect email or password"


@pytest.mark.asyncio
async def test_get_current_user_me(client, db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.create_user("user@morphe.edu", "password123", "Alice")

    token = create_access_token(str(user.id))
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "user@morphe.edu"


@pytest.mark.asyncio
async def test_update_profile(client, db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.create_user("user@morphe.edu", "password123", "Alice")

    token = create_access_token(str(user.id))
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.patch(
        "/api/v1/users/me", headers=headers, json={"full_name": "Alice Cooper"}
    )
    assert response.status_code == 200
    assert response.json()["full_name"] == "Alice Cooper"


@pytest.mark.asyncio
async def test_change_password(client, db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.create_user("user@morphe.edu", "password123", "Alice")

    token = create_access_token(str(user.id))
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.patch(
        "/api/v1/users/change-password",
        headers=headers,
        json={"old_password": "password123", "new_password": "new_secure_password_99"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_rbac_admin_routes(client, db_session):
    user_repo = UserRepository(db_session)
    admin = await user_repo.create_user("admin@morphe.edu", "adminpass", "Admin User", role="admin")
    researcher = await user_repo.create_user(
        "researcher@morphe.edu", "pass1", "Researcher User", role="researcher"
    )

    admin_token = create_access_token(str(admin.id))
    res_token = create_access_token(str(researcher.id))

    # Researcher attempts to access admin route -> Forbidden (403)
    response = await client.get(
        "/api/v1/admin/users", headers={"Authorization": f"Bearer {res_token}"}
    )
    assert response.status_code == 403

    # Admin accesses admin route -> OK (200)
    response = await client.get(
        "/api/v1/admin/users", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) >= 2


@pytest.mark.asyncio
async def test_token_refresh_rotation(client, db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.create_user("user@morphe.edu", "password123", "Alice")

    refresh_token = create_refresh_token(str(user.id))
    expires_at = datetime.datetime.now(datetime.timezone.utc).replace(
        tzinfo=None
    ) + datetime.timedelta(days=7)

    # Insert token record into database
    rt_record = RefreshTokenDb(
        id=uuid.uuid4(),
        user_id=user.id,
        token=refresh_token,
        expires_at=expires_at,
        is_revoked=False,
    )
    db_session.add(rt_record)
    await db_session.commit()

    # Call refresh endpoint
    response = await client.post(f"/api/v1/auth/refresh?refresh_token={refresh_token}")
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    # Ensure old token is revoked (rotation check)
    await db_session.refresh(rt_record)
    assert rt_record.is_revoked is True
