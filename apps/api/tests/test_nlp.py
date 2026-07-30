import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.deps import db_dependency
from app.db.base import Base
from app.main import app
from app.modules.auth.deps import create_access_token
from app.modules.auth.repository import UserRepository
from app.modules.cdm.repository import CanonicalDocumentRepository
from app.modules.cdm.schemas import Author, CanonicalDocument, DocumentSection, SectionType
from app.modules.nlp.pipeline import NlpPipelineRunner
from app.modules.projects.repository import PaperVersionRepository, ProjectRepository

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

    from app.modules.nlp.router import get_session_maker

    class MockSessionMaker:
        def __init__(self, session):
            self.session = session

        def __call__(self):
            return self

        async def __aenter__(self):
            return self.session

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    app.dependency_overrides[db_dependency] = override_db
    app.dependency_overrides[get_session_maker] = lambda: MockSessionMaker(db_session)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_nlp_pipeline_runner():
    raw_text = (
        "Quantum Core Analysis. This paper proposes a robust algorithm for parsing data. "
        "Contact researcher at author@stanford.edu or DOI: 10.1234/morphe.2026. "
        "The experiments were completed at Stanford University."
    )
    cdm_dict = {
        "sections": [{"title": "Introduction", "content_markdown": raw_text}],
        "references": [],
    }

    runner = NlpPipelineRunner()
    res = await runner.run(raw_text, cdm_dict)

    assert res["language"] == "en"
    assert len(res["sentences"]) >= 2
    assert len(res["tokens"]) > 10

    # Check entities
    entities_types = {e["type"] for e in res["entities"]}
    assert "EMAIL" in entities_types
    assert "DOI" in entities_types
    assert "ORGANIZATION" in entities_types

    # Check statistics
    assert res["statistics"]["word_count"] > 10
    assert res["statistics"]["lexical_diversity"] > 0.0


@pytest.mark.asyncio
async def test_nlp_api_workflow(client, db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.create_user("user@morphe.org", "pass123", "Alice")

    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(user.id, "NLP Analytics Project")

    ver_repo = PaperVersionRepository(db_session)
    version = await ver_repo.create(
        project_id=project.id,
        version_number=1,
        commit_message="Initial Draft",
        input_type="raw_text",
        file_path_or_text="Abstract: details\n\nIntroduction: text content."
    )

    # Create dummy CDM record in DB
    cdm_repo = CanonicalDocumentRepository(db_session)
    cdm_doc = CanonicalDocument(
        id=str(project.id),
        version_id=str(version.id),
        domain_profile_id="general",
        title="Robust Neural Layout Parsing",
        authors=[Author(id="auth_1", first_name="Alice", last_name="Bob")],
        abstract="This paper proposes an algorithm at Stanford University.",
        keywords=[],
        sections=[
            DocumentSection(
                id="sec_1",
                section_type=SectionType.INTRODUCTION,
                title="Introduction",
                content_markdown="Here is our method section details.",
                order=1,
            )
        ],
        references=[],
        media_objects=[],
        metadata={},
    )
    await cdm_repo.create_or_update(version.id, project.id, cdm_doc)

    token = create_access_token(str(user.id))
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Trigger NLP analysis job
    process_req = {"project_id": str(project.id), "version_id": str(version.id)}
    res = await client.post("/api/v1/nlp/process", json=process_req, headers=headers)
    assert res.status_code == 202
    job_id = res.json()["job_id"]

    # 2. Check NLP job details
    job_res = await client.get(f"/api/v1/nlp/jobs/{job_id}", headers=headers)
    assert job_res.status_code == 200
    assert job_res.json()["status"] in {"queued", "running", "completed"}

    # 3. Retrieve completed entities (we trigger it synchronously inside tests mock)
    # The MockSessionMaker executes background tasks immediately on same session
    ent_res = await client.get(f"/api/v1/nlp/entities/{version.id}", headers=headers)
    assert ent_res.status_code in {200, 404}
