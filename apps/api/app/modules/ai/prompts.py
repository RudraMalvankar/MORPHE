from typing import Dict, List, Optional

from app.modules.ai.schemas import CitationStyle, PaperType, SectionType

PAPER_TYPE_STRUCTURES: Dict[PaperType, List[SectionType]] = {
    PaperType.RESEARCH_ARTICLE: [
        SectionType.INTRODUCTION,
        SectionType.METHODOLOGY,
        SectionType.RESULTS,
        SectionType.DISCUSSION,
        SectionType.CONCLUSION,
    ],
    PaperType.REVIEW_ARTICLE: [
        SectionType.INTRODUCTION,
        SectionType.LITERATURE_REVIEW,
        SectionType.DISCUSSION,
        SectionType.CONCLUSION,
    ],
    PaperType.SYSTEMATIC_REVIEW: [
        SectionType.INTRODUCTION,
        SectionType.METHODOLOGY,
        SectionType.RESULTS,
        SectionType.DISCUSSION,
        SectionType.CONCLUSION,
    ],
    PaperType.META_ANALYSIS: [
        SectionType.INTRODUCTION,
        SectionType.METHODOLOGY,
        SectionType.RESULTS,
        SectionType.DISCUSSION,
        SectionType.CONCLUSION,
    ],
    PaperType.CASE_STUDY: [
        SectionType.INTRODUCTION,
        SectionType.METHODOLOGY,
        SectionType.RESULTS,
        SectionType.DISCUSSION,
        SectionType.CONCLUSION,
    ],
    PaperType.POSITION_PAPER: [
        SectionType.INTRODUCTION,
        SectionType.LITERATURE_REVIEW,
        SectionType.DISCUSSION,
        SectionType.CONCLUSION,
    ],
    PaperType.CONFERENCE_PAPER: [
        SectionType.INTRODUCTION,
        SectionType.METHODOLOGY,
        SectionType.RESULTS,
        SectionType.DISCUSSION,
    ],
    PaperType.THEORETICAL_PAPER: [
        SectionType.INTRODUCTION,
        SectionType.LITERATURE_REVIEW,
        SectionType.DISCUSSION,
        SectionType.CONCLUSION,
    ],
    PaperType.METHODOLOGICAL_PAPER: [
        SectionType.INTRODUCTION,
        SectionType.LITERATURE_REVIEW,
        SectionType.METHODOLOGY,
        SectionType.RESULTS,
        SectionType.CONCLUSION,
    ],
    PaperType.LITERATURE_REVIEW: [
        SectionType.INTRODUCTION,
        SectionType.LITERATURE_REVIEW,
        SectionType.DISCUSSION,
        SectionType.CONCLUSION,
    ],
    PaperType.TECHNICAL_REPORT: [
        SectionType.INTRODUCTION,
        SectionType.METHODOLOGY,
        SectionType.RESULTS,
        SectionType.DISCUSSION,
        SectionType.CONCLUSION,
    ],
    PaperType.THESIS: [
        SectionType.INTRODUCTION,
        SectionType.LITERATURE_REVIEW,
        SectionType.METHODOLOGY,
        SectionType.RESULTS,
        SectionType.DISCUSSION,
        SectionType.CONCLUSION,
    ],
    PaperType.WHITE_PAPER: [
        SectionType.INTRODUCTION,
        SectionType.LITERATURE_REVIEW,
        SectionType.DISCUSSION,
        SectionType.CONCLUSION,
    ],
}

PAPER_TYPE_DESCRIPTIONS: Dict[PaperType, str] = {
    PaperType.RESEARCH_ARTICLE: "An original empirical research paper following the IMRaD structure (Introduction, Methods, Results, and Discussion). Presents new findings from original research.",
    PaperType.REVIEW_ARTICLE: "A comprehensive review that synthesizes existing research on a specific topic. Does not present new experimental data but provides critical analysis and synthesis.",
    PaperType.SYSTEMATIC_REVIEW: "A rigorous, reproducible review following PRISMA guidelines. Uses systematic search strategy to identify, select, and critically appraise all relevant studies.",
    PaperType.META_ANALYSIS: "A quantitative statistical analysis that combines results from multiple independent studies to determine overall effect sizes and draw broader conclusions.",
    PaperType.CASE_STUDY: "An in-depth examination of a specific instance, event, individual, or organization to illustrate broader principles or generate insights.",
    PaperType.POSITION_PAPER: "Presents a clear stance on a debatable issue, supported by evidence and logical arguments. Acknowledges and rebuts counterarguments.",
    PaperType.CONFERENCE_PAPER: "A condensed version of research presented at an academic conference. Typically shorter and more focused than a full journal article.",
    PaperType.THEORETICAL_PAPER: "Explores, critiques, or proposes new theoretical frameworks or conceptual models. Does not collect original data.",
    PaperType.METHODOLOGICAL_PAPER: "Introduces or evaluates a new research method, technique, or approach. Includes validation and comparison with existing methods.",
    PaperType.LITERATURE_REVIEW: "A comprehensive overview of existing literature in a particular area, summarizing and synthesizing research findings to identify trends and gaps.",
    PaperType.TECHNICAL_REPORT: "A detailed report on technical research or development work. Includes methodology, findings, and practical recommendations.",
    PaperType.THESIS: "A long-form academic document presenting original research as part of a graduate or doctoral degree. Multiple chapters with comprehensive coverage.",
    PaperType.WHITE_PAPER: "An authoritative report that identifies a problem and proposes a solution. Often used in business and policy contexts.",
}

CITATION_STYLE_DESCRIPTIONS: Dict[CitationStyle, str] = {
    CitationStyle.APA: "American Psychological Association 7th edition. Uses author-date in-text citations like (Author, Year). Reference list is alphabetical. Standard for psychology, education, and social sciences.",
    CitationStyle.MLA: "Modern Language Association 9th edition. Uses author-page in-text citations like (Author Page). Works Cited list is alphabetical. Standard for humanities and literature.",
    CitationStyle.CHICAGO: "Chicago Manual of Style 17th edition. Offers two systems: Notes-Bibliography (footnotes) and Author-Date. Used in history, arts, and general scholarship.",
    CitationStyle.IEEE: "Institute of Electrical and Electronics Engineers. Uses numbered bracketed citations [1]. Reference list is ordered by appearance. Standard for engineering and computer science.",
    CitationStyle.HARVARD: "An author-date referencing system similar to APA but with local variations. Widely used in UK and Australian universities across disciplines.",
    CitationStyle.VANCOUVER: "A numbered system used in medicine and life sciences. Uses superscript or bracketed numbers. Reference list follows citation order.",
    CitationStyle.AMA: "American Medical Association 11th edition. Uses superscript numbered citations. Standard for medical and health sciences journals.",
    CitationStyle.ACS: "American Chemical Society. Supports both numbered and author-date systems. Standard for chemistry journals.",
    CitationStyle.TURABIAN: "A simplified version of Chicago style designed for students. Uses footnotes or author-date citations. Common for student papers and theses.",
}


def get_system_instruction(paper_type: PaperType) -> str:
    return f"""You are an expert academic writer and researcher specializing in {PAPER_TYPE_DESCRIPTIONS[paper_type]}.

Your task is to write high-quality, publication-ready academic content that:
- Uses formal, precise academic language
- Follows the structural conventions of {paper_type.value.replace('_', ' ')} papers
- Includes proper hedging language where appropriate
- Uses clear topic sentences and logical paragraph flow
- Avoids colloquialisms and informal language
- Maintains objectivity and scholarly tone
- Includes specific details and examples to support claims
- Uses transitions between paragraphs and sections
- Follows the conventions of the target citation style"""


def get_title_generation_prompt(
    topic: str,
    keywords: List[str],
    paper_type: PaperType,
    research_domain: str,
) -> str:
    keyword_str = ", ".join(keywords) if keywords else "N/A"
    return f"""Generate 3 compelling academic paper titles for the following research:

Topic: {topic}
Keywords: {keyword_str}
Paper Type: {paper_type.value.replace('_', ' ')}
Research Domain: {research_domain}

Requirements:
- Titles should be concise (10-15 words max)
- Use title case
- Be specific and informative
- Include key terms from the research area
- Avoid abbreviations and jargon in titles

Return ONLY the 3 titles, one per line, without numbering or additional text."""


def get_abstract_generation_prompt(
    title: str,
    topic: str,
    keywords: List[str],
    paper_type: PaperType,
    sections_content: Optional[Dict[str, str]] = None,
) -> str:
    keyword_str = ", ".join(keywords) if keywords else "N/A"
    sections_context = ""
    if sections_content:
        sections_context = "\n\nExisting sections for context:\n"
        for sec_name, sec_content in sections_content.items():
            sections_context += f"\n{sec_name.upper()}:\n{sec_content[:1000]}...\n"

    return f"""Write a structured abstract for this academic paper:

Title: {title}
Topic: {topic}
Keywords: {keyword_str}
Paper Type: {paper_type.value.replace('_', ' ')}
{sections_context}

The abstract MUST follow this structured format (if applicable to the paper type):

{get_abstract_structure(paper_type)}

Requirements:
- Be concise (150-300 words)
- Include the purpose/objective of the study
- Describe the methodology used
- Summarize key findings or arguments
- State the main conclusions and implications
- Use past tense for completed actions
- Avoid citations in the abstract
- Include keywords at the end"""


def get_abstract_structure(paper_type: PaperType) -> str:
    structures = {
        PaperType.RESEARCH_ARTICLE: """Structure:
- Background: Brief context and problem statement
- Methods: Describe the research approach
- Results: Present key findings with specific data
- Conclusion: Main implications and significance""",
        PaperType.REVIEW_ARTICLE: """Structure:
- Background: Context and review scope
- Methods: Search strategy and selection criteria
- Synthesis: Key themes and findings from literature
- Conclusions: Main insights and future directions""",
        PaperType.SYSTEMATIC_REVIEW: """Structure:
- Background: Rationale and objectives
- Methods: Database search, inclusion/exclusion criteria
- Results: Number of studies included, key findings
- Conclusions: Implications and recommendations""",
        PaperType.CASE_STUDY: """Structure:
- Background: Context and significance of the case
- Case Description: Brief overview of the case
- Findings/Analysis: Key observations and insights
- Conclusions: Broader implications and lessons""",
    }
    return structures.get(paper_type, structures[PaperType.RESEARCH_ARTICLE])


def get_section_generation_prompt(
    section_type: SectionType,
    title: str,
    topic: str,
    paper_type: PaperType,
    abstract: str = "",
    previous_sections: Optional[Dict[str, str]] = None,
    methodology_type: Optional[str] = None,
    additional_instructions: Optional[str] = None,
    citation_style: CitationStyle = CitationStyle.IEEE,
) -> str:
    context = f"Title: {title}\nTopic: {topic}\nPaper Type: {paper_type.value.replace('_', ' ')}\n"
    if abstract:
        context += f"Abstract: {abstract}\n"

    if previous_sections:
        context += "\nPrevious sections (for coherence and flow):\n"
        for sec_name, sec_content in previous_sections.items():
            context += f"\n{sec_name.upper()} (last 500 chars):\n{sec_content[-500:]}\n"

    if additional_instructions:
        context += f"\nAdditional instructions: {additional_instructions}\n"

    return f"""{context}

Write the {section_type.value.replace('_', ' ').title()} section for this academic paper.

Section-specific requirements:

{get_section_requirements(section_type, paper_type, citation_style)}

General requirements:
- Use formal academic language
- Maintain logical flow from previous sections
- Use topic sentences for paragraphs
- Include transitions between paragraphs
- Be specific and evidence-based
- Use hedging language where appropriate (e.g., "suggests", "indicates", "appears to")
- Target length: {get_section_target_length(section_type, paper_type)}

Write ONLY the section content. Do not include the section heading (it will be added automatically)."""


def get_section_requirements(
    section_type: SectionType,
    paper_type: PaperType,
    citation_style: CitationStyle,
) -> str:
    requirements = {
        SectionType.INTRODUCTION: """- Open with a compelling hook or broad context statement
- Narrow down to the specific research problem
- Review key background literature briefly
- Clearly state the research question/objective/hypothesis
- Explain the significance and contribution of this work
- Outline the paper structure (optional for journal articles)
- Use the CARS (Create a Research Space) model:
  1. Establish territory (general topic importance)
  2. Establish a niche (identify gaps)
  3. Occupy the niche (state contribution)""",
        SectionType.METHODOLOGY: """- Describe the research design/approach
- Explain data collection methods and procedures
- Describe the sample/participants/data sources
- Detail the analysis methods/tools used
- Address ethical considerations if applicable
- Justify methodological choices
- Ensure reproducibility by providing sufficient detail
- Use past tense for completed actions""",
        SectionType.RESULTS: """- Present findings objectively without interpretation
- Use clear subheadings for different aspects of results
- Include quantitative data with appropriate statistics
- Reference tables and figures appropriately
- Report effect sizes and confidence intervals
- Present results in logical order
- Do not repeat methodology details
- Highlight key findings""",
        SectionType.DISCUSSION: """- Interpret findings in context of research questions
- Compare with existing literature and prior studies
- Explain unexpected or contradictory results
- Discuss implications (theoretical and practical)
- Address limitations of the study
- Avoid simply restating results
- Use hedging language for interpretations
- Connect back to the introduction""",
        SectionType.CONCLUSION: """- Summarize main findings/arguments concisely
- Restate the significance and contribution
- Discuss practical implications
- Suggest specific future research directions
- End with a strong concluding statement
- Do not introduce new information or evidence
- Keep it concise (typically 10-15% of paper)""",
        SectionType.LITERATURE_REVIEW: """- Organize thematically, chronologically, or methodologically
- Synthesize (don't just summarize) the literature
- Identify patterns, trends, and contradictions
- Evaluate methodological quality of reviewed studies
- Highlight research gaps that your work addresses
- Use critical analysis, not just description
- Maintain logical flow between themes
- Connect reviews to your research question""",
        SectionType.FUTURE_WORK: """- Suggest specific, actionable research directions
- Address limitations identified in the discussion
- Propose methodological improvements
- Identify emerging areas for investigation
- Be realistic and specific, not vague
- Connect suggestions to your findings""",
        SectionType.ACKNOWLEDGEMENTS: """- Acknowledge funding sources with grant numbers
- Thank colleagues who provided assistance
- Acknowledge institutional support
- Mention data sources or facilities used
- Keep it brief and professional""",
    }
    return requirements.get(section_type, "Write this section according to standard academic conventions for the paper type.")


def get_section_target_length(section_type: SectionType, paper_type: PaperType) -> str:
    lengths = {
        PaperType.RESEARCH_ARTICLE: {
            SectionType.INTRODUCTION: "800-1200 words",
            SectionType.METHODOLOGY: "800-1500 words",
            SectionType.RESULTS: "800-1500 words",
            SectionType.DISCUSSION: "1000-1500 words",
            SectionType.CONCLUSION: "300-500 words",
            SectionType.LITERATURE_REVIEW: "N/A",
        },
        PaperType.CONFERENCE_PAPER: {
            SectionType.INTRODUCTION: "300-500 words",
            SectionType.METHODOLOGY: "300-500 words",
            SectionType.RESULTS: "300-500 words",
            SectionType.DISCUSSION: "300-500 words",
        },
        PaperType.THESIS: {
            SectionType.INTRODUCTION: "3000-5000 words",
            SectionType.METHODOLOGY: "3000-5000 words",
            SectionType.RESULTS: "5000-8000 words",
            SectionType.DISCUSSION: "3000-5000 words",
            SectionType.CONCLUSION: "1000-2000 words",
            SectionType.LITERATURE_REVIEW: "5000-8000 words",
        },
    }
    type_lengths = lengths.get(paper_type, lengths[PaperType.RESEARCH_ARTICLE])
    return type_lengths.get(section_type, "500-1000 words")


def get_conversion_prompt(
    source_content: str,
    target_paper_type: PaperType,
    target_publisher: str,
    target_citation_style: CitationStyle,
) -> str:
    return f"""You are an expert academic paper format converter. Convert the following academic paper content into the specified format.

TARGET FORMAT:
- Paper Type: {target_paper_type.value.replace('_', ' ')}
- Publisher: {target_publisher.upper()}
- Citation Style: {CITATION_STYLE_DESCRIPTIONS.get(target_citation_style, 'Standard academic')}

CONVERSION RULES:
1. Restructure the content to match {target_paper_type.value.replace('_', ' ')} conventions
2. Reformat all citations to {target_citation_style.value.upper()} style
3. Adjust section headings and structure as needed
4. Ensure proper academic tone and formatting
5. Add/remove sections as required by the target format
6. Adjust word counts and level of detail as appropriate
7. Maintain all original content and meaning
8. Preserve all references but reformat them

SOURCE CONTENT:
{source_content}

Return the converted paper with clear section headings. Include a title, abstract, all required sections, and properly formatted references."""


def get_refine_prompt(
    section_type: SectionType,
    current_content: str,
    feedback: str,
) -> str:
    return f"""Refine the following {section_type.value.replace('_', ' ').title()} section based on the provided feedback.

CURRENT CONTENT:
{current_content}

FEEDBACK:
{feedback}

Requirements:
- Address all points in the feedback
- Maintain academic tone and style
- Keep the same general structure unless feedback suggests otherwise
- Improve clarity, flow, and academic rigor
- Preserve valid content while incorporating improvements

Return ONLY the refined section content."""


def get_keywords_generation_prompt(title: str, abstract: str, research_domain: str) -> str:
    return f"""Generate 5-8 relevant academic keywords for this paper:

Title: {title}
Abstract: {abstract}
Research Domain: {research_domain}

Requirements:
- Keywords should be specific and relevant
- Include both broad and narrow terms
- Use standard academic terminology
- Avoid abbreviations unless commonly used
- Cover the main topics and methods

Return ONLY the keywords, separated by commas, without numbering or additional text."""


def get_data_analysis_prompt(
    research_question: str,
    data_description: str,
    paper_type: PaperType,
) -> str:
    return f"""Based on the following research context, suggest appropriate statistical analyses and describe what results would look like:

Research Question: {research_question}
Data Description: {data_description}
Paper Type: {paper_type.value.replace('_', ' ')}

Provide:
1. Recommended statistical tests with justification
2. Expected result formats (tables, figures)
3. How to report results in academic writing
4. Potential limitations of the analysis
5. Alternative analyses if assumptions are violated"""
