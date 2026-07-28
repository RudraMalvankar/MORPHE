# MORPHE Architecture Reference Guide

This document summarizes the Frozen Architecture Version 1.0 for MORPHE.

## Architectural Lifecycle

```
Understand -> Structure -> Validate -> Transform -> Publish
```

## Storage Isolation
- **Layer 1**: Original Inputs (raw PDF/DOCX binaries, plain text inputs)
- **Layer 2**: Canonical Document Model (CDM JSON AST & Version Snapshots)
- **Layer 3**: Generated Artifacts (DOCX, Typst PDF, LaTeX, HTML deliverables)

## Domain Modules & Event Bus
All backend modules communicate via typed Domain Events (`DocumentIngestedEvent`, `CDMUpdatedEvent`, `ValidationCompletedEvent`, `ExportRequestedEvent`). Direct cross-module DB queries are strictly prohibited.

## Plugin & Exporter Abstractions
- **Plugin API v1**: Standardized base driver `BaseJournalPluginV1` for IEEE, Springer, Elsevier, ACM, and Nature formatters.
- **Unified Exporter**: Abstract exporter `BaseExporter` implemented by `DocxExporter`, `PdfExporter`, `LaTeXExporter`, and `HtmlExporter`.
