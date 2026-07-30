import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Set


class NlpPipelineStage(ABC):
    @abstractmethod
    async def process(
        self, text_content: str, cdm_data: Dict[str, Any], artifact: Dict[str, Any]
    ) -> None:
        """Executes processing step on text modifying the target output artifact."""
        pass


class DocumentNormalizationStage(NlpPipelineStage):
    async def process(
        self, text_content: str, cdm_data: Dict[str, Any], artifact: Dict[str, Any]
    ) -> None:
        # Unicode normalization, control chars removal, spacing clean (Part 2)
        normalized = text_content.encode("ascii", "ignore").decode("utf-8")
        normalized = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        artifact["normalized_text"] = normalized


class SentenceSegmentationStage(NlpPipelineStage):
    async def process(
        self, text_content: str, cdm_data: Dict[str, Any], artifact: Dict[str, Any]
    ) -> None:
        text = artifact.get("normalized_text", text_content)
        # Academic sentence splitter protecting abbreviations (Part 3)
        sentence_regex = re.compile(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s")
        sentences = sentence_regex.split(text)

        sentence_list = []
        for i, s in enumerate(sentences):
            s = s.strip()
            if len(s) > 1:
                sentence_list.append({"id": i + 1, "text": s})
        artifact["sentences"] = sentence_list


class TokenizationStage(NlpPipelineStage):
    async def process(
        self, text_content: str, cdm_data: Dict[str, Any], artifact: Dict[str, Any]
    ) -> None:
        # Tokenizer tracking offset coordinates, sentence tags (Part 4)
        sentences = artifact.get("sentences", [])
        token_list = []
        token_id = 1

        for s in sentences:
            sentence_id = s["id"]
            sentence_text = s["text"]

            # Extract word components
            words = re.findall(r"\b\w+\b|[^\w\s]", sentence_text)
            for idx, word in enumerate(words):
                token_list.append(
                    {"id": token_id, "text": word, "sentence_id": sentence_id, "position": idx}
                )
                token_id += 1
        artifact["tokens"] = token_list


class LanguageDetectionStage(NlpPipelineStage):
    async def process(
        self, text_content: str, cdm_data: Dict[str, Any], artifact: Dict[str, Any]
    ) -> None:
        # Vocabulary Stop Words Match Strategy (Part 5)
        text_lower = text_content.lower()
        english_stopwords = {
            "the",
            "and",
            "of",
            "to",
            "in",
            "is",
            "that",
            "for",
            "it",
            "on",
            "with",
            "as",
        }
        words = re.findall(r"\b[a-z]+\b", text_lower)

        stop_count = sum(1 for w in words if w in english_stopwords)
        total_words = len(words) or 1
        density = stop_count / total_words

        if density > 0.05:
            artifact["language"] = "en"
            artifact["language_confidence"] = min(1.0, density * 5.0)
        else:
            artifact["language"] = "en"  # default
            artifact["language_confidence"] = 0.5


class LemmatizationStopwordsStage(NlpPipelineStage):
    async def process(
        self, text_content: str, cdm_data: Dict[str, Any], artifact: Dict[str, Any]
    ) -> None:
        # Stop-words and Lemmatizer stage (Part 6)
        stopwords = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "is",
            "are",
            "was",
            "were",
            "to",
            "of",
            "in",
            "at",
            "by",
            "for",
        }
        tokens = artifact.get("tokens", [])

        processed_tokens = []
        for t in tokens:
            t_text = t["text"]
            t_lower = t_text.lower()

            is_stop = t_lower in stopwords

            # Basic lemmatizer mapping (e.g. plurals, basic tense)
            lemma = t_lower
            if t_lower.endswith("ies") and len(t_lower) > 5:
                lemma = t_lower[:-3] + "y"
            elif t_lower.endswith("es") and not t_lower.endswith("ees") and len(t_lower) > 4:
                lemma = t_lower[:-2]
            elif (
                t_lower.endswith("s")
                and not t_lower.endswith("ss")
                and not t_lower.endswith("us")
                and len(t_lower) > 3
            ):
                lemma = t_lower[:-1]
            elif t_lower.endswith("ing") and len(t_lower) > 5:
                lemma = t_lower[:-3]
            elif t_lower.endswith("ed") and len(t_lower) > 4:
                lemma = t_lower[:-2]

            processed_tokens.append({**t, "lemma": lemma, "is_stopword": is_stop})
        artifact["tokens"] = processed_tokens


class PosTaggingStage(NlpPipelineStage):
    async def process(
        self, text_content: str, cdm_data: Dict[str, Any], artifact: Dict[str, Any]
    ) -> None:
        # Rule-based parts-of-speech assigner (Part 7)
        tokens = artifact.get("tokens", [])
        tagged_tokens = []

        nouns = {
            "university",
            "college",
            "algorithm",
            "dataset",
            "framework",
            "analysis",
            "system",
            "method",
            "model",
            "data",
        }
        verbs = {
            "propose",
            "evaluate",
            "implement",
            "create",
            "test",
            "develop",
            "analyze",
            "run",
            "compute",
            "show",
        }
        adjectives = {
            "efficient",
            "novel",
            "robust",
            "high",
            "new",
            "experimental",
            "significant",
            "accurate",
            "safe",
        }

        for t in tokens:
            lemma = t.get("lemma", t["text"].lower())
            pos = "Noun"
            if lemma in nouns:
                pos = "Noun"
            elif lemma in verbs:
                pos = "Verb"
            elif lemma in adjectives:
                pos = "Adjective"
            elif lemma in {"the", "a", "an"}:
                pos = "Determiner"
            elif lemma in {"and", "or", "but"}:
                pos = "Conjunction"

            tagged_tokens.append({**t, "pos_tag": pos})
        artifact["tokens"] = tagged_tokens


class NamedEntityRecognitionStage(NlpPipelineStage):
    async def process(
        self, text_content: str, cdm_data: Dict[str, Any], artifact: Dict[str, Any]
    ) -> None:
        # Named Entities extractors (Part 8)
        text = artifact.get("normalized_text", text_content)
        entities = []

        # Regex mappings
        email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
        doi_pattern = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", re.IGNORECASE)
        orcid_pattern = re.compile(r"\b\d{4}-\d{4}-\d{4}-\d{3}[0-9X]\b")
        url_pattern = re.compile(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+")

        for match in email_pattern.finditer(text):
            entities.append({"text": match.group(), "type": "EMAIL", "confidence": 1.0})
        for match in doi_pattern.finditer(text):
            entities.append({"text": match.group(), "type": "DOI", "confidence": 1.0})
        for match in orcid_pattern.finditer(text):
            entities.append({"text": match.group(), "type": "ORCID", "confidence": 1.0})
        for match in url_pattern.finditer(text):
            entities.append({"text": match.group(), "type": "URL", "confidence": 1.0})

        # Match Universities & Algorithms
        univ_matches = re.finditer(r"\b[A-Z][a-zA-Z\s]+ (University|Institute|College)\b", text)
        for match in univ_matches:
            entities.append({"text": match.group(), "type": "ORGANIZATION", "confidence": 0.85})

        algo_keywords = {
            "algorithm",
            "network",
            "transformer",
            "resnet",
            "classifier",
            "optimizer",
            "backpropagation",
        }
        for word in re.findall(r"\b[A-Za-z\-]{3,}\b", text):
            if word.lower() in algo_keywords:
                entities.append({"text": word, "type": "ALGORITHM", "confidence": 0.75})

        # Deduplicate entities
        seen: Set[str] = set()
        dedup_entities = []
        for ent in entities:
            key = f"{ent['text']}_{ent['type']}"
            if key not in seen:
                seen.add(key)
                dedup_entities.append(ent)
        artifact["entities"] = dedup_entities


class KeywordExtractionStage(NlpPipelineStage):
    async def process(
        self, text_content: str, cdm_data: Dict[str, Any], artifact: Dict[str, Any]
    ) -> None:
        # TF-IDF / Vocabulary frequency-based keyword ranking (Part 9)
        tokens = artifact.get("tokens", [])
        freq: Dict[str, int] = {}
        for t in tokens:
            if not t.get("is_stopword", False) and len(t["text"]) > 4:
                word = t["text"].lower()
                freq[word] = freq.get(word, 0) + 1

        sorted_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        keywords_output = []
        for kw, score in sorted_keywords[:10]:
            keywords_output.append({"keyword": kw, "score": float(score)})
        artifact["keywords"] = keywords_output


class CitationDetectionStage(NlpPipelineStage):
    async def process(
        self, text_content: str, cdm_data: Dict[str, Any], artifact: Dict[str, Any]
    ) -> None:
        # Numerical bracket/inline citation markers detection (Part 10)
        text = artifact.get("normalized_text", text_content)
        citation_markers = re.findall(r"\[\d+\]", text)

        # Link mapped citation objects to CDM references index (Part 10 reference link)
        citations_map = []
        cdm_refs = cdm_data.get("references", [])

        for marker in set(citation_markers):
            num = re.search(r"\d+", marker)
            if num:
                idx = int(num.group()) - 1
                if 0 <= idx < len(cdm_refs):
                    target_id = cdm_refs[idx].get("id", f"ref_{idx + 1}")
                    citations_map.append({"marker": marker, "target_ref_id": target_id})
        artifact["citation_mappings"] = citations_map


class SectionClassificationStage(NlpPipelineStage):
    async def process(
        self, text_content: str, cdm_data: Dict[str, Any], artifact: Dict[str, Any]
    ) -> None:
        # Section structures classifier (Part 11)
        cdm_sections = cdm_data.get("sections", [])
        classifications = []

        mapping_keys = {
            "introduction": "Introduction",
            "abstract": "Abstract",
            "method": "Methodology",
            "experiment": "Experiments",
            "result": "Results",
            "discussion": "Discussion",
            "conclusion": "Conclusion",
            "reference": "References",
            "appendix": "Appendix",
        }

        for sec in cdm_sections:
            title = sec.get("title", "")
            lower_title = title.lower()
            classified_type = "Other"

            for key, val in mapping_keys.items():
                if key in lower_title:
                    classified_type = val
                    break

            classifications.append(
                {
                    "section_title": title,
                    "classified_type": classified_type,
                    "confidence": 1.0 if classified_type != "Other" else 0.5,
                }
            )
        artifact["section_classifications"] = classifications


class StatisticalAnalysisStage(NlpPipelineStage):
    async def process(
        self, text_content: str, cdm_data: Dict[str, Any], artifact: Dict[str, Any]
    ) -> None:
        # Numeric vocabulary density computations (Part 12)
        tokens = artifact.get("tokens", [])
        sentences = artifact.get("sentences", [])
        words = [t for t in tokens if t["text"].isalnum()]

        word_count = len(words)
        sentence_count = len(sentences) or 1
        vocab = {t["text"].lower() for t in tokens if t["text"].isalnum()}

        avg_sentence_len = word_count / sentence_count
        lexical_diversity = len(vocab) / (word_count or 1)

        # Assume 200 WPM reading speed
        reading_time = word_count / 200.0

        artifact["statistics"] = {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "paragraph_count": len(cdm_data.get("sections", [])) * 2,
            "section_count": len(cdm_data.get("sections", [])),
            "avg_sentence_length": float(avg_sentence_len),
            "lexical_diversity": float(lexical_diversity),
            "vocabulary_size": len(vocab),
            "reading_time_mins": float(reading_time),
        }


class NlpPipelineRunner:
    def __init__(self):
        self.stages: List[NlpPipelineStage] = [
            DocumentNormalizationStage(),
            SentenceSegmentationStage(),
            TokenizationStage(),
            LanguageDetectionStage(),
            LemmatizationStopwordsStage(),
            PosTaggingStage(),
            NamedEntityRecognitionStage(),
            KeywordExtractionStage(),
            CitationDetectionStage(),
            SectionClassificationStage(),
            StatisticalAnalysisStage(),
        ]

    async def run(self, text: str, cdm_dict: Dict[str, Any]) -> Dict[str, Any]:
        artifact: Dict[str, Any] = {}
        for stage in self.stages:
            await stage.process(text, cdm_dict, artifact)
        return artifact
