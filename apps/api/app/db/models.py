import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# ==========================================
# PART 4 - REUSABLE AUDIT MIXINS
# ==========================================


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class SoftDeleteMixin:
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class AuditMixin:
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)


class VersionMixin:
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)


# ==========================================
# USER & PROJECT MODELS (LAYER 2 CORE)
# ==========================================


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="researcher", nullable=False)

    projects: Mapped[List["Project"]] = relationship(
        "Project", back_populates="user", cascade="all, delete-orphan"
    )


class Project(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    default_publisher_target: Mapped[str] = mapped_column(
        String(100), default="ieee", nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="projects")
    versions: Mapped[List["PaperVersion"]] = relationship(
        "PaperVersion", back_populates="project", cascade="all, delete-orphan"
    )


class PaperVersion(Base, TimestampMixin, VersionMixin):
    __tablename__ = "paper_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    commit_message: Mapped[str] = mapped_column(String(255), nullable=False)

    # Future Engines Metadata Placeholders (Part 8)
    detected_domain: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    detected_subdomain: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    detected_research_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    detected_publication_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    detected_citation_style: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    readiness_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    quality_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="versions")
    original_inputs: Mapped[List["OriginalInput"]] = relationship(
        "OriginalInput", back_populates="paper_version", cascade="all, delete-orphan"
    )
    canonical_documents: Mapped[List["CanonicalDocumentDb"]] = relationship(
        "CanonicalDocumentDb", back_populates="paper_version", cascade="all, delete-orphan"
    )
    validation_reports: Mapped[List["ValidationReport"]] = relationship(
        "ValidationReport", back_populates="paper_version", cascade="all, delete-orphan"
    )
    export_artifacts: Mapped[List["ExportArtifact"]] = relationship(
        "ExportArtifact", back_populates="paper_version", cascade="all, delete-orphan"
    )
    journal_recommendations: Mapped[List["JournalRecommendation"]] = relationship(
        "JournalRecommendation", back_populates="paper_version", cascade="all, delete-orphan"
    )


# ==========================================
# LAYER 1: ORIGINAL INPUTS
# ==========================================


class OriginalInput(Base, TimestampMixin):
    __tablename__ = "original_inputs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("paper_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    input_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_path_or_text: Mapped[str] = mapped_column(String, nullable=False)

    paper_version: Mapped["PaperVersion"] = relationship(
        "PaperVersion", back_populates="original_inputs"
    )


# ==========================================
# LAYER 2: CANONICAL DOCUMENT MODEL (CDM)
# ==========================================


class CanonicalDocumentDb(Base, TimestampMixin, VersionMixin):
    __tablename__ = "canonical_documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("paper_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    cdm_data: Mapped[dict] = mapped_column(JSON, nullable=False)

    paper_version: Mapped["PaperVersion"] = relationship(
        "PaperVersion", back_populates="canonical_documents"
    )


class ValidationReport(Base, TimestampMixin):
    __tablename__ = "validation_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("paper_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    compliance_score: Mapped[int] = mapped_column(Integer, nullable=False)
    issues_json: Mapped[dict] = mapped_column(JSON, nullable=False)

    paper_version: Mapped["PaperVersion"] = relationship(
        "PaperVersion", back_populates="validation_reports"
    )


# ==========================================
# LAYER 3: GENERATED EXPORT ARTIFACTS
# ==========================================


class ExportArtifact(Base, TimestampMixin):
    __tablename__ = "export_artifacts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("paper_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    publisher_key: Mapped[str] = mapped_column(String(100), nullable=False)
    export_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)

    paper_version: Mapped["PaperVersion"] = relationship(
        "PaperVersion", back_populates="export_artifacts"
    )


# ==========================================
# PART 8 - FUTURE ENGINES SCHEMA SUPPORT
# ==========================================


class JournalRecommendation(Base, TimestampMixin):
    __tablename__ = "journal_recommendations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("paper_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    journal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    publisher_key: Mapped[str] = mapped_column(String(100), nullable=False)
    compatibility_score: Mapped[int] = mapped_column(Integer, nullable=False)
    match_reasons: Mapped[dict] = mapped_column(JSON, nullable=False)

    paper_version: Mapped["PaperVersion"] = relationship(
        "PaperVersion", back_populates="journal_recommendations"
    )


# ==========================================
# PART 2 - ENHANCED DOMAIN PROFILES
# ==========================================


class DomainProfileDb(Base, TimestampMixin, VersionMixin):
    __tablename__ = "domain_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_domain_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    required_sections: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)
    optional_sections: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)
    expected_citation_style: Mapped[str] = mapped_column(String(100), nullable=False)
    supported_publishers: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)
    recommended_journals: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)
    research_types: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)
    validation_rules: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)
    transformation_rules: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)
    nlp_extensions: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)
    research_terminology: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)
    required_metadata: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)
    submission_requirements: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)

    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)


# ==========================================
# PART 1 - ACADEMIC KNOWLEDGE BASE MODELS
# ==========================================


class Publisher(Base, TimestampMixin):
    __tablename__ = "kb_publishers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    journals: Mapped[List["Journal"]] = relationship(
        "Journal", back_populates="publisher", cascade="all, delete-orphan"
    )


class Journal(Base, TimestampMixin):
    __tablename__ = "kb_journals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    publisher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("kb_publishers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    impact_factor: Mapped[Optional[float]] = mapped_column(nullable=True)
    scope_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    publisher: Mapped["Publisher"] = relationship("Publisher", back_populates="journals")


class Conference(Base, TimestampMixin):
    __tablename__ = "kb_conferences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    core_rank: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)


class CitationStyle(Base, TimestampMixin):
    __tablename__ = "kb_citation_styles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    rules_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class FormattingRule(Base, TimestampMixin):
    __tablename__ = "kb_formatting_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    rules_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class SubmissionGuideline(Base, TimestampMixin):
    __tablename__ = "kb_submission_guidelines"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    guidelines_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class DomainTaxonomy(Base, TimestampMixin):
    __tablename__ = "kb_domain_taxonomies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    taxonomy_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class ResearchStructure(Base, TimestampMixin):
    __tablename__ = "kb_research_structures"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    structure_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class ValidationRuleKb(Base, TimestampMixin):
    __tablename__ = "kb_validation_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    rules_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class PublisherPolicy(Base, TimestampMixin):
    __tablename__ = "kb_publisher_policies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    policy_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class KnowledgeBaseEntry(Base, TimestampMixin):
    __tablename__ = "knowledge_base_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # "publishers", "journals"
    key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    value: Mapped[dict] = mapped_column(JSON, nullable=False)


class RefreshTokenDb(Base, TimestampMixin):
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token: Mapped[str] = mapped_column(String(512), unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class StorageObject(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "storage_objects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("paper_versions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    storage_provider: Mapped[str] = mapped_column(String(50), default="local", nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), default="active", nullable=False
    )  # active, deleted, archived


class IngestionJobDb(Base, TimestampMixin):
    __tablename__ = "ingestion_jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("paper_versions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("storage_objects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50), default="queued", nullable=False, index=True
    )  # queued, running, completed, failed, cancelled
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)


class NlpDocumentDb(Base, TimestampMixin):
    __tablename__ = "nlp_documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("paper_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    language: Mapped[str] = mapped_column(String(50), default="en", nullable=False)
    language_confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    processed_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )


class NlpEntityDb(Base, TimestampMixin):
    __tablename__ = "nlp_entities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("nlp_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    entity_text: Mapped[str] = mapped_column(String(512), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)


class NlpKeywordDb(Base, TimestampMixin):
    __tablename__ = "nlp_keywords"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("nlp_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    keyword: Mapped[str] = mapped_column(String(255), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)


class NlpStatisticsDb(Base, TimestampMixin):
    __tablename__ = "nlp_statistics"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("nlp_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    word_count: Mapped[int] = mapped_column(Integer, nullable=False)
    sentence_count: Mapped[int] = mapped_column(Integer, nullable=False)
    paragraph_count: Mapped[int] = mapped_column(Integer, nullable=False)
    section_count: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_sentence_length: Mapped[float] = mapped_column(Float, nullable=False)
    lexical_diversity: Mapped[float] = mapped_column(Float, nullable=False)
    vocabulary_size: Mapped[int] = mapped_column(Integer, nullable=False)
    reading_time_mins: Mapped[float] = mapped_column(Float, nullable=False)


class NlpCitationMapDb(Base, TimestampMixin):
    __tablename__ = "nlp_citation_maps"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("nlp_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    citation_marker: Mapped[str] = mapped_column(String(100), nullable=False)
    target_ref_id: Mapped[str] = mapped_column(String(100), nullable=False)


class NlpSectionClassificationDb(Base, TimestampMixin):
    __tablename__ = "nlp_section_classifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("nlp_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    section_title: Mapped[str] = mapped_column(String(255), nullable=False)
    classified_type: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)


class NlpJobDb(Base, TimestampMixin):
    __tablename__ = "nlp_jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("paper_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(50), default="queued", nullable=False, index=True)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
