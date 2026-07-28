import uuid

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.models import (
    User,
)
from app.modules.cdm.repository import CanonicalDocumentRepository
from app.modules.cdm.schemas import (
    Author,
    CanonicalDocument,
    DocumentSection,
    SectionType,
)
from app.modules.export.repository import ExportArtifactRepository
from app.modules.knowledge.repository import DomainProfileRepository, KnowledgeBaseRepository
from app.modules.projects.repository import PaperVersionRepository, ProjectRepository
from app.modules.validator.repository import ValidationReportRepository

# Setup async memory SQLite engine for isolated testing
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


@pytest.mark.asyncio
async def test_create_user_and_project(db_session: AsyncSession):
    # Setup mock user
    user = User(
        id=uuid.uuid4(),
        email="test_author@morphe.edu",
        password_hash="argon2_hashed_secret",
        full_name="Dr. Jane Doe",
    )
    db_session.add(user)
    await db_session.commit()

    # Verify Project Repository
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(
        user_id=user.id,
        title="Universal Quantum Computing on Edge Devices",
        description="A comprehensive analysis of quantum layouts",
        default_publisher_target="ieee",
    )

    assert project.id is not None
    assert project.title == "Universal Quantum Computing on Edge Devices"
    assert project.user_id == user.id


@pytest.mark.asyncio
async def test_paper_version_and_cdm_repositories(db_session: AsyncSession):
    # Setup user & project
    user = User(
        id=uuid.uuid4(), email="author@morphe.edu", password_hash="hash", full_name="Author"
    )
    db_session.add(user)
    await db_session.commit()

    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(user_id=user.id, title="Test Project")

    # Verify Version Repository & Ingestion Event emitting flow
    version_repo = PaperVersionRepository(db_session)
    version = await version_repo.create(
        project_id=project.id,
        version_number=1,
        commit_message="Initial ingestion",
        input_type="raw_text",
        file_path_or_text="Abstract: This paper introduces MORPHE...",
    )

    assert version.version_number == 1

    # Create valid Pydantic CDM instance
    author = Author(id="auth_1", first_name="Jane", last_name="Doe", affiliations=["MIT"])
    section = DocumentSection(
        id="sec_1",
        section_type=SectionType.INTRODUCTION,
        title="Introduction",
        content_markdown="Start here",
        order=1,
    )

    cdm_doc = CanonicalDocument(
        id=str(project.id),
        version_id=str(version.id),
        domain_profile_id="computer_science",
        title="Test Project Title",
        authors=[author],
        abstract="This is the abstract text.",
        keywords=["quantum", "computing"],
        sections=[section],
        references=[],
        media_objects=[],
    )

    # Verify CDM Repository
    cdm_repo = CanonicalDocumentRepository(db_session)
    cdm_db = await cdm_repo.create_or_update(version.id, project.id, cdm_doc)

    assert cdm_db.version_id == version.id

    # Fetch back and validate
    fetched_doc = await cdm_repo.get_by_version(version.id)
    assert fetched_doc is not None
    assert fetched_doc.title == "Test Project Title"
    assert fetched_doc.domain_profile_id == "computer_science"
    assert len(fetched_doc.authors) == 1
    assert fetched_doc.authors[0].first_name == "Jane"


@pytest.mark.asyncio
async def test_validation_and_export_repositories(db_session: AsyncSession):
    user = User(
        id=uuid.uuid4(), email="author2@morphe.edu", password_hash="hash", full_name="Author"
    )
    db_session.add(user)
    await db_session.commit()

    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(user_id=user.id, title="Validation Project")

    version_repo = PaperVersionRepository(db_session)
    version = await version_repo.create(
        project_id=project.id,
        version_number=1,
        commit_message="Verifying exports",
        input_type="form",
        file_path_or_text="{}",
    )

    # Validation Report Repository
    val_repo = ValidationReportRepository(db_session)
    report = await val_repo.create(
        version_id=version.id,
        project_id=project.id,
        compliance_score=95,
        issues={"warnings": ["Missing ORCID"]},
    )
    assert report.compliance_score == 95

    # Export Artifact Repository
    export_repo = ExportArtifactRepository(db_session)
    artifact = await export_repo.create(
        version_id=version.id,
        publisher_key="ieee",
        export_type="pdf",
        file_path="exports/ieee_version_1.pdf",
    )
    assert artifact.publisher_key == "ieee"
    assert artifact.export_type == "pdf"


@pytest.mark.asyncio
async def test_knowledge_base_and_domain_profiles(db_session: AsyncSession):
    profile_repo = DomainProfileRepository(db_session)
    profile = await profile_repo.create_or_update(
        key="medicine",
        display_name="Clinical Medicine Profile",
        data={"required_sections": ["Abstract", "Introduction", "Methodology", "Results"]},
    )

    assert profile.key == "medicine"
    assert profile.display_name == "Clinical Medicine Profile"

    kb_repo = KnowledgeBaseRepository(db_session)
    entry = await kb_repo.create_or_update_entry(
        category="citation_styles",
        key="vancouver",
        value={"format": "numeric", "bracket": "parenthesis"},
    )

    assert entry.category == "citation_styles"
    assert entry.key == "vancouver"
