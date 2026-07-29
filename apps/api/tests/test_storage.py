import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.deps import db_dependency
from app.db.base import Base
from app.main import app
from app.modules.auth.deps import create_access_token
from app.modules.auth.repository import UserRepository
from app.modules.projects.repository import PaperVersionRepository, ProjectRepository
from app.modules.storage.provider import LocalStorageProvider

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

    app.dependency_overrides[db_dependency] = override_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_storage_provider_traversal():
    provider = LocalStorageProvider(root_dir="temp_storage")
    with pytest.raises(ValueError, match="Directory traversal attempt blocked"):
        provider._get_absolute_path("../outside_root.txt")


@pytest.mark.asyncio
async def test_file_upload_and_download(client, db_session):
    # Setup users and projects
    user_repo = UserRepository(db_session)
    user = await user_repo.create_user("user@morphe.edu", "pass123", "Alice")

    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(user.id, "Quantum Analysis")

    token = create_access_token(str(user.id))
    headers = {"Authorization": f"Bearer {token}"}

    # Perform upload
    file_payload = {"file": ("paper.pdf", b"Dummy PDF file content bytes", "application/pdf")}
    response = await client.post(
        f"/api/v1/storage/upload?project_id={project.id}", headers=headers, files=file_payload
    )
    assert response.status_code == 201
    upload_data = response.json()
    assert upload_data["original_filename"] == "paper.pdf"
    assert upload_data["mime_type"] == "application/pdf"
    assert upload_data["file_size"] > 0
    file_id = upload_data["id"]

    # Perform download
    download_res = await client.get(f"/api/v1/storage/files/{file_id}/download", headers=headers)
    assert download_res.status_code == 200
    assert download_res.content == b"Dummy PDF file content bytes"


@pytest.mark.asyncio
async def test_upload_blocked_extension(client, db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.create_user("user@morphe.edu", "pass123", "Alice")

    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(user.id, "Quantum Analysis")

    token = create_access_token(str(user.id))
    headers = {"Authorization": f"Bearer {token}"}

    file_payload = {"file": ("malicious.exe", b"executable bytes", "application/octet-stream")}
    response = await client.post(
        f"/api/v1/storage/upload?project_id={project.id}", headers=headers, files=file_payload
    )
    assert response.status_code == 400
    assert "not allowed" in response.json()["detail"]


@pytest.mark.asyncio
async def test_file_ownership_permissions(client, db_session):
    user_repo = UserRepository(db_session)
    alice = await user_repo.create_user("alice@morphe.edu", "pass123", "Alice")
    bob = await user_repo.create_user("bob@morphe.edu", "pass123", "Bob")

    proj_repo = ProjectRepository(db_session)
    alice_project = await proj_repo.create(alice.id, "Alice Research")

    alice_token = create_access_token(str(alice.id))
    bob_token = create_access_token(str(bob.id))

    # Bob tries to upload to Alice's project -> Forbidden (403)
    file_payload = {"file": ("data.txt", b"plain text", "text/plain")}
    response = await client.post(
        f"/api/v1/storage/upload?project_id={alice_project.id}",
        headers={"Authorization": f"Bearer {bob_token}"},
        files=file_payload,
    )
    assert response.status_code == 403

    # Alice uploads successfully
    response = await client.post(
        f"/api/v1/storage/upload?project_id={alice_project.id}",
        headers={"Authorization": f"Bearer {alice_token}"},
        files=file_payload,
    )
    assert response.status_code == 201
    file_id = response.json()["id"]

    # Bob tries to download Alice's file -> Forbidden (403)
    download_res = await client.get(
        f"/api/v1/storage/files/{file_id}/download",
        headers={"Authorization": f"Bearer {bob_token}"},
    )
    assert download_res.status_code == 403


@pytest.mark.asyncio
async def test_version_restore(client, db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.create_user("user@morphe.edu", "pass123", "Alice")

    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(user.id, "Quantum Analysis")

    version_repo = PaperVersionRepository(db_session)
    ver = await version_repo.create(project.id, 1, "First version", "raw_text", "Initial source")

    token = create_access_token(str(user.id))
    headers = {"Authorization": f"Bearer {token}"}

    file_payload = {"file": ("paper.tex", b"LaTeX source", "application/x-latex")}
    response = await client.post(
        f"/api/v1/storage/upload?project_id={project.id}&version_id={ver.id}",
        headers=headers,
        files=file_payload,
    )
    assert response.status_code == 201
    file_id = response.json()["id"]

    # Deleting the file
    del_res = await client.delete(f"/api/v1/storage/files/{file_id}", headers=headers)
    assert del_res.status_code == 200

    # Restoring the file back to the version
    restore_res = await client.patch(
        f"/api/v1/storage/files/{file_id}/restore?target_version_id={ver.id}", headers=headers
    )
    assert restore_res.status_code == 200
    assert restore_res.json()["file_id"] == file_id
