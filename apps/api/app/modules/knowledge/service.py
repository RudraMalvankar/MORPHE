from typing import Dict, List, Optional

from app.modules.knowledge.data.citations import list_citation_styles
from app.modules.knowledge.data.guidelines import list_all_guidelines
from app.modules.knowledge.data.metrics import JOURNAL_METRICS
from app.modules.knowledge.schemas import (
    CitationEntry,
    KBEntryResponse,
    KBSearchRequest,
    KBSearchResponse,
)


class KnowledgeBaseService:
    def __init__(self):
        self._guidelines_cache: Optional[Dict] = None
        self._citations_cache: Optional[Dict] = None
        self._metrics_cache: Optional[Dict] = None

    def _load_guidelines(self) -> Dict:
        if self._guidelines_cache is None:
            self._guidelines_cache = list_all_guidelines()
        return self._guidelines_cache

    def _load_citations(self) -> Dict:
        if self._citations_cache is None:
            self._citations_cache = list_citation_styles()
        return self._citations_cache

    def _load_metrics(self) -> Dict:
        if self._metrics_cache is None:
            self._metrics_cache = JOURNAL_METRICS
        return self._metrics_cache

    async def get_publisher_guidelines(self, publisher_key: str) -> Optional[Dict]:
        guidelines = self._load_guidelines()
        return guidelines.get(publisher_key)

    async def list_all_guidelines(self) -> Dict:
        return self._load_guidelines()

    async def get_citation_style(self, style_key: str) -> Optional[Dict]:
        styles = self._load_citations()
        return styles.get(style_key)

    async def list_citation_styles(self) -> Dict:
        return self._load_citations()

    async def get_journal_metrics(self, journal_key: str) -> Optional[Dict]:
        metrics = self._load_metrics()
        return metrics.get(journal_key)

    async def list_journals(self, publisher_key: Optional[str] = None) -> List[Dict]:
        metrics = self._load_metrics()
        journals = list(metrics.values())
        if publisher_key:
            journals = [j for j in journals if j["publisher_key"] == publisher_key]
        return journals

    async def search(self, request: KBSearchRequest) -> KBSearchResponse:
        results: List[KBEntryResponse] = []

        if request.category is None or request.category.value == "publisher_guidelines":
            guidelines = self._load_guidelines()
            for key, value in guidelines.items():
                if not request.publisher_key or value.get("publisher_key") == request.publisher_key:
                    if not request.query or request.query.lower() in str(value).lower():
                        results.append(
                            KBEntryResponse(
                                id=f"guidelines_{key}",
                                category="publisher_guidelines",
                                key=key,
                                value=value,
                            )
                        )

        if request.category is None or request.category.value == "citation_styles":
            styles = self._load_citations()
            for key, value in styles.items():
                if not request.query or request.query.lower() in str(value).lower():
                    results.append(
                        KBEntryResponse(
                            id=f"citation_{key}",
                            category="citation_styles",
                            key=key,
                            value=value,
                        )
                    )

        if request.category is None or request.category.value == "journal_metrics":
            metrics = self._load_metrics()
            for key, value in metrics.items():
                if not request.publisher_key or value.get("publisher_key") == request.publisher_key:
                    if not request.query or request.query.lower() in str(value).lower():
                        results.append(
                            KBEntryResponse(
                                id=f"metrics_{key}",
                                category="journal_metrics",
                                key=key,
                                value=value,
                            )
                        )

        return KBSearchResponse(
            results=results[:request.limit],
            total=len(results),
            query=request.query,
        )

    async def format_citation(
        self, citation: CitationEntry, style: str, index: int = 1
    ) -> str:
        style_config = await self.get_citation_style(style)
        if not style_config:
            return ""

        fmt = style_config.get("reference_format", "")
        authors_str = ", ".join(citation.authors[:6])

        return fmt.format(
            index=index,
            authors=authors_str,
            title=citation.title,
            journal=citation.journal,
            volume=citation.volume,
            issue=citation.issue,
            pages=citation.pages,
            year=citation.year,
            doi=citation.doi,
        )
