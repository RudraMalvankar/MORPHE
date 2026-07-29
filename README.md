# MORPHE — AI-Powered Universal Research Document Intelligence & Publishing Platform

MORPHE is a universal, cross-disciplinary research intelligence and publishing platform designed to automate, normalize, and assist the academic publishing lifecycle from raw draft to print-ready publisher templates.

Unlike traditional single-purpose tools, MORPHE bridges the gap between authors and publishers by providing real-time compliance validation, structural restructuring (e.g., IMRaD standards), and automated formatting engines across every academic discipline.

---

## 🌟 Why MORPHE is Being Built

Academic publishing is plagued by format friction, compliance complexity, and administrative delays. Authors spend countless hours manually adapting citations, formatting layouts, and checking style guidelines for different publishers (e.g., IEEE, Elsevier, Nature, ACM).

MORPHE solves this by introducing:
* **Discipline Agnosticism**: Supports research document structure mapping for computer science, medical journals, legal briefs, humanities, and physics.
* **Format Compliance & Validation**: Automatically matches paper drafts against target publisher policies, reporting structural and citation compliance scores.
* **Layout Portability**: Translates structured documents into clean, publisher-compliant PDFs, LaTeX packages, and DOCX formats without losing semantic integrity.

---

## 🏗️ Core Architecture & Features

MORPHE follows a **Modular Monolith** pattern built around a frozen architectural core:

* **Canonical Document Model (CDM)**: An Abstract Syntax Tree (AST) representing a document's semantic structure (metadata, authors, sections, media objects, references) rather than layout properties.
* **Three-Layer Storage Model**:
  * **Layer 1 (Original Inputs)**: Raw uploads of PDFs, LaTeX source files, DOCX, Markdown, supplementary images, or datasets.
  * **Layer 2 (Canonical Documents)**: Version-controlled, immutable CDM snapshots stored in native JSONB format.
  * **Layer 3 (Generated Artifacts)**: Compiled output packages (Typst, PDF, LaTeX, HTML) aligned with publisher styles.
* **Identity & Access Management (IAM)**: Production-grade Token-based authentication using **JWT** with Token Rotation, revocation, and Role-Based Access Control (RBAC) (Admin, Researcher, Reviewer, Editor, Guest).
* **Domain Event Bus**: Enforces asynchronous event coupling (e.g., `DocumentIngestedEvent`, `FileUploadedEvent`, `CDMUpdatedEvent`).

---

## 💻 Tech Stack

### Frontend Application
* **Framework**: Next.js 15 (App Router) & React 19 (Strict Mode)
* **Language**: TypeScript
* **Styling**: Tailwind CSS & Vanilla CSS (Tailored HSL theme variables)
* **Components**: Radix UI Primitives (`shadcn/ui`)
* **State Management**: Zustand & TanStack Query v5

### Backend Core
* **Framework**: FastAPI (Async ASGI)
* **ORM**: SQLAlchemy 2.0 (Async)
* **Validation**: Pydantic v2 (Strict typing)
* **Migration**: Alembic
* **Authentication**: PyJWT (HS256 with JWT JTI Claims) & bcrypt password salting
* **Databases**: PostgreSQL 16 (Structured data) & Redis (ARQ async task queue caching)
* **File Operations**: Asynchronous I/O via `aiofiles` and SHA-256 integrity checksums

### Ingestion & Compilation Engines
* **Scientific PDF Parsing**: GROBID (Docker sidecar running ML citation parsing)
* **NLP Pipeline**: spaCy, NLTK, Sentence Transformers, and KeyBERT
* **PDF Compiler**: Typst (Modern high-fidelity typesetting compiler)

---

## 📂 Project Structure

```
MORPHE/
├── apps/
│   ├── api/                       # FastAPI Backend
│   │   ├── app/
│   │   │   ├── api/v1/            # Health and System Routing
│   │   │   ├── core/              # Global Configuration, Security, Logger & Redis
│   │   │   ├── db/                # SQLAlchemy models, sessions, base repositories
│   │   │   └── modules/           # Modular domains
│   │   │       ├── auth/          # IAM module (JWT, password hash, RBAC endpoints)
│   │   │       ├── cdm/           # Canonical Document Model schemas and JSON handlers
│   │   │       ├── export/        # Export logging repository
│   │   │       ├── knowledge/     # Academic database models and configs
│   │   │       ├── projects/      # Core projects and version management
│   │   │       ├── storage/       # Three-Layer storage and upload routing
│   │   │       └── validator/     # Quality validation loggers
│   │   └── tests/                 # Full Integration Pytest suite (Aiosqlite)
│   └── web/                       # Next.js Front-end portal
├── docker/                        # Multi-container local environments
├── docs/                          # Technical Design Documents (TDD)
├── package.json                   # Workspaces config (npm/pnpm)
└── docker-compose.yml             # System compose services (FastAPI, NextJS, Postgres, Redis, Grobid)
```

---

## 🚀 Getting Started

### Prerequisites
* Docker & Docker Compose
* Node.js 18+ & npm/pnpm
* Python 3.11+

### Running Locally with Docker
1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
2. Start the services:
   ```bash
   docker-compose up --build
   ```
3. Access the services:
   * **API Swagger Docs**: `http://localhost:8000/docs`
   * **Next.js Web Portal**: `http://localhost:3000`

### Running Backend Tests
1. Navigate to the API workspace:
   ```bash
   cd apps/api
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the async test suite:
   ```bash
   python -m pytest tests/
   ```
