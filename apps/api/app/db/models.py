import uuid
from typing import List, Optional

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    projects: Mapped[List["Project"]] = relationship(
        "Project", back_populates="user", cascade="all, delete-orphan"
    )


class Project(Base):
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
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="projects")
    versions: Mapped[List["PaperVersion"]] = relationship(
        "PaperVersion", back_populates="project", cascade="all, delete-orphan"
    )


class PaperVersion(Base):
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

    project: Mapped["Project"] = relationship("Project", back_populates="versions")
    original_inputs: Mapped[List["OriginalInput"]] = relationship(
        "OriginalInput", back_populates="version", cascade="all, delete-orphan"
    )
    canonical_documents: Mapped[List["CanonicalDocumentDb"]] = relationship(
        "CanonicalDocumentDb", back_populates="version", cascade="all, delete-orphan"
    )
    validation_reports: Mapped[List["ValidationReport"]] = relationship(
        "ValidationReport", back_populates="version", cascade="all, delete-orphan"
    )
    export_artifacts: Mapped[List["ExportArtifact"]] = relationship(
        "ExportArtifact", back_populates="version", cascade="all, delete-orphan"
    )


class OriginalInput(Base):
    __tablename__ = "original_inputs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("paper_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    input_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # "raw_text", "pdf", "docx", "form"
    file_path_or_text: Mapped[str] = mapped_column(String, nullable=False)

    version: Mapped["PaperVersion"] = relationship("PaperVersion", back_populates="original_inputs")


class CanonicalDocumentDb(Base):
    __tablename__ = "canonical_documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("paper_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    cdm_data: Mapped[dict] = mapped_column(JSON, nullable=False)

    version: Mapped["PaperVersion"] = relationship(
        "PaperVersion", back_populates="canonical_documents"
    )


class ValidationReport(Base):
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

    version: Mapped["PaperVersion"] = relationship(
        "PaperVersion", back_populates="validation_reports"
    )


class ExportArtifact(Base):
    __tablename__ = "export_artifacts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("paper_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    publisher_key: Mapped[str] = mapped_column(String(100), nullable=False)
    export_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # "docx", "pdf", "latex", "html"
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)

    version: Mapped["PaperVersion"] = relationship(
        "PaperVersion", back_populates="export_artifacts"
    )


class DomainProfileDb(Base):
    __tablename__ = "domain_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    data: Mapped[dict] = mapped_column(JSON, nullable=False)


class KnowledgeBaseEntry(Base):
    __tablename__ = "knowledge_base_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # "publishers", "journals", "citation_styles"
    key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    value: Mapped[dict] = mapped_column(JSON, nullable=False)
