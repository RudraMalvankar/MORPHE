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
from app.modules.domain.pipeline import DomainPipelineRunner
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

    from app.modules.domain.router import get_session_maker

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
async def test_domain_pipeline_runner():
    raw_text = (
        "Quantum Computing Core Analysis. "
        "This paper proposes a robust algorithm for network routing. "
        "We evaluate neural architectures for deep learning tasks."
    )
    cdm_dict = {
        "sections": [
            {"title": "Introduction", "content_markdown": raw_text},
            {"title": "Methodology", "content_markdown": "Evaluation data details."},
        ],
        "references": [],
    }
    nlp_dict = {
        "keywords": [{"keyword": "algorithm", "score": 5}],
        "entities": [{"entity_text": "Stanford University", "entity_type": "ORGANIZATION"}],
    }

    runner = DomainPipelineRunner()
    res = await runner.run(raw_text, cdm_dict, nlp_dict, {})

    assert res["primary_domain"] == "Computer Science"
    assert res["subdomain"] == "Machine Learning"
    assert res["research_type"] == "Experimental"
    assert res["citation_style"] == "ACM"
    assert len(res["terminology"]) > 0
    assert res["structure_analysis"]["is_order_correct"] is False  # missing sections


@pytest.mark.asyncio
async def test_domain_api_workflow(client, db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.create_user("analyst@morphe.edu", "pass123", "Alice")

    proj_repo = ProjectRepository(db_session)
    project = await proj_repo.create(user.id, "Domain Inferences")

    ver_repo = PaperVersionRepository(db_session)
    version = await ver_repo.create(
        project_id=project.id,
        version_number=1,
        commit_message="Domain verification",
        input_type="raw_text",
        file_path_or_text="Details for quantum mechanics routing.",
    )

    cdm_repo = CanonicalDocumentRepository(db_session)
    cdm_doc = CanonicalDocument(
        id=str(project.id),
        version_id=str(version.id),
        domain_profile_id="general",
        title="Robust Quantum Logic Gates",
        authors=[Author(id="auth_1", first_name="Bob", last_name="Alice")],
        abstract="This paper introduces quantum physics algorithms.",
        keywords=[],
        sections=[
            DocumentSection(
                id="sec_1",
                section_type=SectionType.INTRODUCTION,
                title="Introduction",
                content_markdown="Intro details.",
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

    # 1. Trigger Domain analysis
    process_req = {"project_id": str(project.id), "version_id": str(version.id)}
    res = await client.post("/api/v1/domain/process", json=process_req, headers=headers)
    assert res.status_code == 202
    job_id = res.json()["job_id"]

    # 2. Check Job status
    job_res = await client.get(f"/api/v1/domain/jobs/{job_id}", headers=headers)
    assert job_res.status_code == 200
    assert job_res.json()["status"] in {"queued", "running", "completed"}

    # 3. Retrieve structure details
    struct_res = await client.get(f"/api/v1/domain/structure/{version.id}", headers=headers)
    assert struct_res.status_code in {200, 404}
