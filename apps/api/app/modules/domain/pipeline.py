import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class DomainIntelligenceStage(ABC):
    @abstractmethod
    async def process(
        self,
        text_content: str,
        cdm_data: Dict[str, Any],
        nlp_data: Dict[str, Any],
        kb_data: Dict[str, Any],
        artifact: Dict[str, Any],
    ) -> None:
        """Processes document inputs to enrich the target Domain Intelligence artifact."""
        pass


class DomainDetectionStage(DomainIntelligenceStage):
    async def process(
        self,
        text_content: str,
        cdm_data: Dict[str, Any],
        nlp_data: Dict[str, Any],
        kb_data: Dict[str, Any],
        artifact: Dict[str, Any],
    ) -> None:
        # Academic discipline detection using terminology rules (Part 2)
        text_lower = text_content.lower()

        domain_keywords = {
            "Computer Science": {
                "algorithm",
                "software",
                "network",
                "computing",
                "dataset",
                "neural",
                "programming",
                "code",
            },
            "Physics": {
                "quantum",
                "particle",
                "gravity",
                "energy",
                "mechanics",
                "electron",
                "thermodynamics",
            },
            "Medicine": {
                "patient",
                "clinical",
                "oncology",
                "therapy",
                "disease",
                "treatment",
                "cardiology",
                "medical",
            },
            "Business": {
                "marketing",
                "finance",
                "operations",
                "supply chain",
                "strategy",
                "investment",
                "firm",
            },
            "Economics": {
                "inflation",
                "gdp",
                "market",
                "policy",
                "macroeconomics",
                "microeconomics",
                "trade",
            },
        }

        scores = {}
        for domain, keywords in domain_keywords.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            scores[domain] = matches

        best_domain = max(scores, key=lambda k: scores[k])
        best_score = scores[best_domain]

        artifact["primary_domain"] = best_domain
        artifact["primary_domain_confidence"] = float(
            min(1.0, best_score / 4.0) if best_score > 0 else 0.5
        )


class SubdomainDetectionStage(DomainIntelligenceStage):
    async def process(
        self,
        text_content: str,
        cdm_data: Dict[str, Any],
        nlp_data: Dict[str, Any],
        kb_data: Dict[str, Any],
        artifact: Dict[str, Any],
    ) -> None:
        # Research specialization identification (Part 3)
        text_lower = text_content.lower()
        primary_domain = artifact.get("primary_domain", "Computer Science")

        subdomains_map = {
            "Computer Science": {
                "Machine Learning": {"learning", "neural", "training", "transformer", "epoch"},
                "Cyber Security": {
                    "cryptography",
                    "encryption",
                    "attack",
                    "malware",
                    "vulnerability",
                },
                "Cloud Computing": {
                    "virtualization",
                    "kubernetes",
                    "aws",
                    "infrastructure",
                    "saas",
                },
            },
            "Medicine": {
                "Oncology": {"cancer", "tumor", "carcinoma", "chemotherapy"},
                "Cardiology": {"heart", "coronary", "ventricular", "myocardial"},
            },
        }

        sub_scores = {}
        options = subdomains_map.get(primary_domain, {"General Science": {"science", "research"}})
        for sub, keywords in options.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            sub_scores[sub] = matches

        best_sub = max(sub_scores, key=lambda k: sub_scores[k])
        best_score = sub_scores[best_sub]

        artifact["subdomain"] = best_sub
        artifact["subdomain_confidence"] = float(
            min(1.0, best_score / 3.0) if best_score > 0 else 0.5
        )


class ResearchTypeStage(DomainIntelligenceStage):
    async def process(
        self,
        text_content: str,
        cdm_data: Dict[str, Any],
        nlp_data: Dict[str, Any],
        kb_data: Dict[str, Any],
        artifact: Dict[str, Any],
    ) -> None:
        # Methodology detection (Part 4)
        text_lower = text_content.lower()

        methods = {
            "Experimental": {
                "experiment",
                "evaluation",
                "result",
                "test",
                "measure",
                "performance",
            },
            "Survey": {"survey", "literature", "review", "state of the art", "overview"},
            "Systematic Literature Review": {
                "slr",
                "systematic",
                "screening",
                "inclusion criteria",
                "database search",
            },
            "Case Study": {"case study", "scenario", "organization", "qualitative", "interview"},
        }

        scores = {}
        for method, keywords in methods.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            scores[method] = matches

        best_method = max(scores, key=lambda k: scores[k])
        best_score = scores[best_method]

        artifact["research_type"] = best_method
        artifact["research_type_confidence"] = float(
            min(1.0, best_score / 3.0) if best_score > 0 else 0.5
        )


class PublicationTypeStage(DomainIntelligenceStage):
    async def process(
        self,
        text_content: str,
        cdm_data: Dict[str, Any],
        nlp_data: Dict[str, Any],
        kb_data: Dict[str, Any],
        artifact: Dict[str, Any],
    ) -> None:
        # Publication category classification (Part 5)
        text_lower = text_content.lower()

        pub_types = {
            "Journal Paper": {"journal", "editor", "transactions", "vol.", "issue"},
            "Conference Paper": {
                "proceedings",
                "conference",
                "symposium",
                "workshop",
                "peer-reviewed",
            },
            "Preprint": {"preprint", "arxiv", "biorxiv", "under review"},
        }

        scores = {}
        for ptype, keywords in pub_types.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            scores[ptype] = matches

        best_ptype = max(scores, key=lambda k: scores[k])
        best_score = scores[best_ptype]

        artifact["publication_type"] = best_ptype
        artifact["publication_type_confidence"] = float(
            min(1.0, best_score / 2.0) if best_score > 0 else 0.5
        )


class CitationStyleStage(DomainIntelligenceStage):
    async def process(
        self,
        text_content: str,
        cdm_data: Dict[str, Any],
        nlp_data: Dict[str, Any],
        kb_data: Dict[str, Any],
        artifact: Dict[str, Any],
    ) -> None:
        # Citation style patterns identification (Part 6)
        text_lower = text_content.lower()

        # Check numerical citations e.g. [1], [2] vs parenthetical author-year e.g. (Smith, 2020)
        has_brackets = len(re.findall(r"\[\d+\]", text_lower)) > 1
        has_author_year = len(re.findall(r"\(\w+,\s+\d{4}\)", text_lower)) > 1

        if has_brackets:
            artifact["citation_style"] = "IEEE"
            artifact["citation_style_confidence"] = 0.85
        elif has_author_year:
            artifact["citation_style"] = "APA"
            artifact["citation_style_confidence"] = 0.80
        else:
            artifact["citation_style"] = "ACM"  # default
            artifact["citation_style_confidence"] = 0.5


class TerminologyAnalysisStage(DomainIntelligenceStage):
    async def process(
        self,
        text_content: str,
        cdm_data: Dict[str, Any],
        nlp_data: Dict[str, Any],
        kb_data: Dict[str, Any],
        artifact: Dict[str, Any],
    ) -> None:
        # Extract vocabulary terms and concepts (Part 7)
        # Pull algorithm/org keywords from nlp entities and keywords
        nlp_keywords = nlp_data.get("keywords", [])
        nlp_entities = nlp_data.get("entities", [])

        terminology = []
        for kw in nlp_keywords[:5]:
            terminology.append(
                {"term": kw["keyword"], "frequency": int(kw["score"]), "term_type": "concept"}
            )

        for ent in nlp_entities[:5]:
            terminology.append(
                {
                    "term": ent["entity_text"],
                    "frequency": 1,
                    "term_type": ent["entity_type"].lower(),
                }
            )

        artifact["terminology"] = terminology


class StructuralIntelligenceStage(DomainIntelligenceStage):
    async def process(
        self,
        text_content: str,
        cdm_data: Dict[str, Any],
        nlp_data: Dict[str, Any],
        kb_data: Dict[str, Any],
        artifact: Dict[str, Any],
    ) -> None:
        # Compare sections layout against expected target profile standards (Part 8)
        cdm_sections = cdm_data.get("sections", [])
        detected_sections = {s.get("title", "").lower() for s in cdm_sections}

        # Standard Expected sections for typical research (IMRaD Profile)
        expected_sections = ["introduction", "methodology", "results", "discussion", "conclusion"]

        missing = []
        expected_present = {}
        for esec in expected_sections:
            match_found = any(esec in ds for ds in detected_sections)
            if not match_found:
                missing.append(esec.title())
            else:
                expected_present[esec.title()] = "present"

        extra = []
        for ds in detected_sections:
            if not any(esec in ds for esec in expected_sections):
                extra.append(ds.title())

        artifact["structure_analysis"] = {
            "expected_sections": expected_present,
            "missing_sections": {m: "missing" for m in missing},
            "extra_sections": {ex: "extra" for ex in extra},
            "is_order_correct": len(missing) == 0,
        }


class DomainPipelineRunner:
    def __init__(self):
        self.stages: List[DomainIntelligenceStage] = [
            DomainDetectionStage(),
            SubdomainDetectionStage(),
            ResearchTypeStage(),
            PublicationTypeStage(),
            CitationStyleStage(),
            TerminologyAnalysisStage(),
            StructuralIntelligenceStage(),
        ]

    async def run(
        self, text: str, cdm_dict: Dict[str, Any], nlp_dict: Dict[str, Any], kb_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        artifact: Dict[str, Any] = {}
        for stage in self.stages:
            await stage.process(text, cdm_dict, nlp_dict, kb_dict, artifact)
        return artifact
