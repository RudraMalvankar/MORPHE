import uuid

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.models import (
    CitationStyle,
    Conference,
    DomainTaxonomy,
    FormattingRule,
    Journal,
    Publisher,
    PublisherPolicy,
    ResearchStructure,
    SubmissionGuideline,
    User,
    ValidationRuleKb,
)
from app.modules.cdm.repository import CanonicalDocumentRepository
from app.modules.cdm.schemas import Author, CanonicalDocument, DocumentSection, SectionType
from app.modules.export.repository import ExportArtifactRepository
from app.modules.knowledge.repository import DomainProfileRepository, KnowledgeBaseRepository
from app.modules.projects.repository import PaperVersionRepository, ProjectRepository
from app.modules.validator.repository import ValidationReportRepository

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
    user = User(
        id=uuid.uuid4(),
        email="test_author@morphe.edu",
        password_hash="argon2_hashed_secret",
        full_name="Dr. Jane Doe",
    )
    db_session.add(user)
    await db_session.commit()

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
    user = User(
        id=uuid.uuid4(), email="author@morphe.edu", password_hash="hash", full_name="Author"
    )
    db_session.add(user)
    await db_session.commit()

    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(user_id=user.id, title="Test Project")

    version_repo = PaperVersionRepository(db_session)
    version = await version_repo.create(
        project_id=project.id,
        version_number=1,
        commit_message="Initial ingestion",
        input_type="raw_text",
        file_path_or_text="Abstract: This paper introduces MORPHE...",
    )

    assert version.version_number == 1

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
        research_domain="computer_science",
        research_type="original_research",
    )

    cdm_repo = CanonicalDocumentRepository(db_session)
    cdm_db = await cdm_repo.create_or_update(version.id, project.id, cdm_doc)

    assert cdm_db.version_id == version.id

    fetched_doc = await cdm_repo.get_by_version(version.id)
    assert fetched_doc is not None
    assert fetched_doc.title == "Test Project Title"
    assert fetched_doc.research_domain == "computer_science"
    assert fetched_doc.research_type == "original_research"


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

    val_repo = ValidationReportRepository(db_session)
    report = await val_repo.create(
        version_id=version.id,
        project_id=project.id,
        compliance_score=95,
        issues={"warnings": ["Missing ORCID"]},
    )
    assert report.compliance_score == 95

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
        data={
            "expected_citation_style": "vancouver",
            "required_sections": ["Abstract", "Introduction", "Methodology", "Results"],
        },
    )

    assert profile.key == "medicine"
    assert profile.expected_citation_style == "vancouver"

    kb_repo = KnowledgeBaseRepository(db_session)
    entry = await kb_repo.create_or_update_entry(
        category="citation_styles",
        key="vancouver",
        value={"format": "numeric", "bracket": "parenthesis"},
    )

    assert entry.category == "citation_styles"
    assert entry.key == "vancouver"


@pytest.mark.asyncio
async def test_normalized_academic_knowledge_models(db_session: AsyncSession):
    # Setup rich normalized models representing TDD v1.1 Academic Knowledge Base
    publisher = Publisher(id=uuid.uuid4(), key="elsevier", name="Elsevier Science")
    db_session.add(publisher)
    await db_session.flush()

    journal = Journal(
        id=uuid.uuid4(),
        publisher_id=publisher.id,
        key="lan",
        name="The Lancet",
        impact_factor=202.7,
    )
    db_session.add(journal)

    conference = Conference(id=uuid.uuid4(), key="nips", name="NeurIPS", core_rank="A*")
    db_session.add(conference)

    citation_style = CitationStyle(
        id=uuid.uuid4(),
        key="apa7",
        name="APA 7th Edition",
        rules_json={"name_format": "Author-Year"},
    )
    db_session.add(citation_style)

    formatting_rule = FormattingRule(
        id=uuid.uuid4(), key="double_column", rules_json={"columns": 2}
    )
    db_session.add(formatting_rule)

    guideline = SubmissionGuideline(
        id=uuid.uuid4(), key="nature_guide", guidelines_json={"max_words": 3000}
    )
    db_session.add(guideline)

    taxonomy = DomainTaxonomy(
        id=uuid.uuid4(), key="cs_tax", taxonomy_json={"STEM": ["Computer Science", "Robotics"]}
    )
    db_session.add(taxonomy)

    structure = ResearchStructure(
        id=uuid.uuid4(), key="imrad", structure_json={"order": ["I", "M", "R", "D"]}
    )
    db_session.add(structure)

    validation_rule = ValidationRuleKb(
        id=uuid.uuid4(), key="min_refs", rules_json={"minimum_references": 5}
    )
    db_session.add(validation_rule)

    policy = PublisherPolicy(id=uuid.uuid4(), key="open_access", policy_json={"licensing": "CC-BY"})
    db_session.add(policy)

    await db_session.commit()

    # Query and assert relationships
    assert journal.publisher_id == publisher.id
    assert journal.name == "The Lancet"
    assert conference.core_rank == "A*"
    assert citation_style.key == "apa7"
    assert formatting_rule.key == "double_column"
    assert guideline.key == "nature_guide"
    assert taxonomy.key == "cs_tax"
    assert structure.key == "imrad"
    assert validation_rule.key == "min_refs"
    assert policy.key == "open_access"
