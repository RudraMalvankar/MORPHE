import uuid
from typing import Dict, List

from app.core.logging import logger
from app.modules.ai.client import gemini_client
from app.modules.ai.prompts import (
    PAPER_TYPE_STRUCTURES,
    get_abstract_generation_prompt,
    get_conversion_prompt,
    get_keywords_generation_prompt,
    get_refine_prompt,
    get_section_generation_prompt,
    get_system_instruction,
    get_title_generation_prompt,
)
from app.modules.ai.schemas import (
    ConvertFormatRequest,
    GeneratedSection,
    GenerateFromContentRequest,
    GenerateFromDataRequest,
    GenerateFromScratchRequest,
    GenerationResultResponse,
    PaperType,
    RefineSectionRequest,
    SectionType,
)


class AIService:
    def __init__(self):
        self.client = gemini_client

    async def generate_from_scratch(
        self, request: GenerateFromScratchRequest
    ) -> GenerationResultResponse:
        if not self.client.is_available:
            raise RuntimeError("Gemini API not configured. Set GEMINI_API_KEY in .env.")

        logger.info(f"Starting generation from scratch: {request.topic[:50]}...")

        system_inst = get_system_instruction(request.paper_type)

        title_response = await self.client.generate(
            get_title_generation_prompt(
                request.topic, request.keywords, request.paper_type, request.research_domain
            ),
            system_instruction=system_inst,
        )
        titles = [t.strip() for t in title_response.strip().split("\n") if t.strip()]
        title = titles[0] if titles else request.topic

        abstract = await self.client.generate(
            get_abstract_generation_prompt(
                title, request.topic, request.keywords, request.paper_type
            ),
            system_instruction=system_inst,
        )

        sections_structure = PAPER_TYPE_STRUCTURES.get(
            request.paper_type, PAPER_TYPE_STRUCTURES[PaperType.RESEARCH_ARTICLE]
        )

        generated_sections: List[GeneratedSection] = []
        previous_sections: Dict[str, str] = {}

        for idx, section_type in enumerate(sections_structure):
            if section_type in (SectionType.TITLE, SectionType.ABSTRACT, SectionType.KEYWORDS):
                continue

            logger.info(f"Generating section: {section_type.value}")
            section_content = await self.client.generate(
                get_section_generation_prompt(
                    section_type=section_type,
                    title=title,
                    topic=request.topic,
                    paper_type=request.paper_type,
                    abstract=abstract,
                    previous_sections=previous_sections,
                    methodology_type=request.methodology_type,
                    additional_instructions=request.additional_instructions,
                    citation_style=request.citation_style,
                ),
                system_instruction=system_inst,
            )

            section = GeneratedSection(
                section_type=section_type,
                title=section_type.value.replace("_", " ").title(),
                content=section_content.strip(),
                order=idx + 1,
            )
            generated_sections.append(section)
            previous_sections[section_type.value] = section_content.strip()

        keywords_response = await self.client.generate(
            get_keywords_generation_prompt(title, abstract, request.research_domain),
            system_instruction=system_inst,
        )
        keywords = [k.strip() for k in keywords_response.split(",") if k.strip()]

        return GenerationResultResponse(
            job_id=str(uuid.uuid4()),
            status="completed",
            title=title,
            abstract=abstract.strip(),
            sections=generated_sections,
            keywords=keywords[:8],
            metadata={
                "paper_type": request.paper_type.value,
                "citation_style": request.citation_style.value,
                "target_publisher": request.target_publisher,
                "research_domain": request.research_domain,
                "mode": "from_scratch",
            },
        )

    async def generate_from_content(
        self, request: GenerateFromContentRequest
    ) -> GenerationResultResponse:
        if not self.client.is_available:
            raise RuntimeError("Gemini API not configured. Set GEMINI_API_KEY in .env.")

        logger.info(f"Starting generation from content ({len(request.raw_content)} chars)")

        system_inst = get_system_instruction(request.paper_type)

        parse_prompt = f"""Analyze the following raw content and extract structured information:

CONTENT:
{request.raw_content[:5000]}

Extract and return JSON with these fields:
{{
    "suggested_title": "A compelling academic title",
    "topic": "The main research topic",
    "keywords": ["keyword1", "keyword2", ...],
    "research_domain": "The academic domain",
    "key_findings": ["finding1", "finding2"],
    "methodology": "Description of methods if mentioned",
    "main_arguments": ["argument1", "argument2"]
}}"""

        parsed = await self.client.generate_structured(parse_prompt, system_instruction=system_inst)

        topic = parsed.get("topic", "Academic research topic")
        title = parsed.get("suggested_title", topic)
        keywords = parsed.get("keywords", [])
        research_domain = parsed.get("research_domain", "general")

        abstract = await self.client.generate(
            get_abstract_generation_prompt(title, topic, keywords, request.paper_type),
            system_instruction=system_inst,
        )

        sections_structure = PAPER_TYPE_STRUCTURES.get(
            request.paper_type, PAPER_TYPE_STRUCTURES[PaperType.RESEARCH_ARTICLE]
        )

        generated_sections: List[GeneratedSection] = []
        previous_sections: Dict[str, str] = {}

        content_instruction = f"""
Use the following source material as the basis for this section. Expand, restructure, and polish it into proper academic prose:

SOURCE MATERIAL:
{request.raw_content[:3000]}"""

        for idx, section_type in enumerate(sections_structure):
            if section_type in (SectionType.TITLE, SectionType.ABSTRACT, SectionType.KEYWORDS):
                continue

            logger.info(f"Generating section from content: {section_type.value}")
            section_content = await self.client.generate(
                get_section_generation_prompt(
                    section_type=section_type,
                    title=title,
                    topic=topic,
                    paper_type=request.paper_type,
                    abstract=abstract,
                    previous_sections=previous_sections,
                    additional_instructions=(
                        (request.additional_instructions or "") + content_instruction
                    ),
                    citation_style=request.citation_style,
                ),
                system_instruction=system_inst,
            )

            section = GeneratedSection(
                section_type=section_type,
                title=section_type.value.replace("_", " ").title(),
                content=section_content.strip(),
                order=idx + 1,
            )
            generated_sections.append(section)
            previous_sections[section_type.value] = section_content.strip()

        keywords_response = await self.client.generate(
            get_keywords_generation_prompt(title, abstract, research_domain),
            system_instruction=system_inst,
        )
        all_keywords = [k.strip() for k in keywords_response.split(",") if k.strip()]

        return GenerationResultResponse(
            job_id=str(uuid.uuid4()),
            status="completed",
            title=title,
            abstract=abstract.strip(),
            sections=generated_sections,
            keywords=all_keywords[:8],
            metadata={
                "paper_type": request.paper_type.value,
                "citation_style": request.citation_style.value,
                "target_publisher": request.target_publisher,
                "research_domain": research_domain,
                "mode": "from_content",
            },
        )

    async def convert_format(
        self, request: ConvertFormatRequest
    ) -> GenerationResultResponse:
        if not self.client.is_available:
            raise RuntimeError("Gemini API not configured. Set GEMINI_API_KEY in .env.")

        logger.info(
            f"Starting format conversion to {request.target_publisher}/{request.target_paper_type.value}"
        )

        system_inst = get_system_instruction(request.target_paper_type)

        converted = await self.client.generate(
            get_conversion_prompt(
                request.source_content,
                request.target_paper_type,
                request.target_publisher,
                request.target_citation_style,
            ),
            system_instruction=system_inst,
        )

        parse_sections_prompt = f"""Parse the following converted academic paper into structured sections:

{converted[:5000]}

Return JSON with:
{{
    "title": "paper title",
    "abstract": "abstract text",
    "sections": [
        {{"heading": "section heading", "content": "section content"}},
        ...
    ],
    "keywords": ["kw1", "kw2"]
}}"""

        parsed = await self.client.generate_structured(
            parse_sections_prompt, system_instruction=system_inst
        )

        title = parsed.get("title", "Converted Paper")
        abstract = parsed.get("abstract", "")
        raw_sections = parsed.get("sections", [])

        generated_sections: List[GeneratedSection] = []
        for idx, sec in enumerate(raw_sections):
            section_type = SectionType.INTRODUCTION
            heading_lower = sec.get("heading", "").lower()
            for st in SectionType:
                if st.value.replace("_", " ") in heading_lower or st.value in heading_lower:
                    section_type = st
                    break

            generated_sections.append(
                GeneratedSection(
                    section_type=section_type,
                    title=sec.get("heading", f"Section {idx + 1}"),
                    content=sec.get("content", ""),
                    order=idx + 1,
                )
            )

        keywords = parsed.get("keywords", [])

        return GenerationResultResponse(
            job_id=str(uuid.uuid4()),
            status="completed",
            title=title,
            abstract=abstract,
            sections=generated_sections,
            keywords=keywords,
            metadata={
                "paper_type": request.target_paper_type.value,
                "citation_style": request.target_citation_style.value,
                "target_publisher": request.target_publisher,
                "mode": "convert_format",
            },
        )

    async def refine_section(
        self, request: RefineSectionRequest
    ) -> str:
        if not self.client.is_available:
            raise RuntimeError("Gemini API not configured. Set GEMINI_API_KEY in .env.")

        logger.info(f"Refining section: {request.section_type.value}")

        refined = await self.client.generate(
            get_refine_prompt(request.section_type, request.current_content, request.feedback),
            system_instruction="You are an expert academic editor. Refine the content based on the feedback while maintaining academic rigor and tone.",
        )

        return refined.strip()

    async def generate_keywords(
        self, title: str, abstract: str, research_domain: str
    ) -> List[str]:
        if not self.client.is_available:
            raise RuntimeError("Gemini API not configured. Set GEMINI_API_KEY in .env.")

        response = await self.client.generate(
            get_keywords_generation_prompt(title, abstract, research_domain)
        )
        return [k.strip() for k in response.split(",") if k.strip()][:8]

    async def generate_from_data(
        self,
        request: GenerateFromDataRequest,
        analysis_summary: str,
        tables_description: str,
        figures_description: str,
    ) -> GenerationResultResponse:
        if not self.client.is_available:
            raise RuntimeError("Gemini API not configured. Set GEMINI_API_KEY in .env.")

        logger.info(
            f"Starting data-driven generation: {request.research_question[:50]}..."
        )

        system_inst = get_system_instruction(request.paper_type)

        title_prompt = (
            f"Generate a compelling academic paper title for a data-driven study.\n"
            f"Research Question: {request.research_question}\n"
            f"Domain: {request.research_domain}\n"
            f"Data Summary: {analysis_summary[:500]}"
        )
        title_response = await self.client.generate(
            title_prompt, system_instruction=system_inst
        )
        titles = [
            t.strip() for t in title_response.strip().split("\n") if t.strip()
        ]
        title = titles[0] if titles else request.research_question[:80]

        abstract = await self.client.generate(
            get_abstract_generation_prompt(
                title,
                request.research_question,
                request.variables,
                request.paper_type,
            ),
            system_instruction=system_inst,
        )

        sections_structure = PAPER_TYPE_STRUCTURES.get(
            request.paper_type,
            PAPER_TYPE_STRUCTURES[PaperType.RESEARCH_ARTICLE],
        )

        generated_sections: List[GeneratedSection] = []
        previous_sections: Dict[str, str] = {}

        data_context = (
            f"\n\nDATA ANALYSIS CONTEXT:\n"
            f"Research Question: {request.research_question}\n"
            f"Analysis Summary: {analysis_summary}\n"
            f"Tables: {tables_description}\n"
            f"Figures: {figures_description}\n"
            f"Variables studied: {', '.join(request.variables)}"
        )

        for idx, section_type in enumerate(sections_structure):
            if section_type in (
                SectionType.TITLE,
                SectionType.ABSTRACT,
                SectionType.KEYWORDS,
            ):
                continue

            logger.info(
                f"Generating data-driven section: {section_type.value}"
            )
            section_content = await self.client.generate(
                get_section_generation_prompt(
                    section_type=section_type,
                    title=title,
                    topic=request.research_question,
                    paper_type=request.paper_type,
                    abstract=abstract,
                    previous_sections=previous_sections,
                    additional_instructions=(
                        (request.additional_instructions or "") + data_context
                    ),
                    citation_style=request.citation_style,
                ),
                system_instruction=system_inst,
            )

            section = GeneratedSection(
                section_type=section_type,
                title=section_type.value.replace("_", " ").title(),
                content=section_content.strip(),
                order=idx + 1,
            )
            generated_sections.append(section)
            previous_sections[section_type.value] = section_content.strip()

        keywords_response = await self.client.generate(
            get_keywords_generation_prompt(
                title, abstract, request.research_domain
            ),
            system_instruction=system_inst,
        )
        keywords = [
            k.strip() for k in keywords_response.split(",") if k.strip()
        ]

        return GenerationResultResponse(
            job_id=str(uuid.uuid4()),
            status="completed",
            title=title,
            abstract=abstract.strip(),
            sections=generated_sections,
            keywords=keywords[:8],
            metadata={
                "paper_type": request.paper_type.value,
                "citation_style": request.citation_style.value,
                "target_publisher": request.target_publisher,
                "research_domain": request.research_domain,
                "mode": "from_data",
                "data_id": request.data_id,
            },
        )


ai_service = AIService()
