CITATION_STYLES = {
    "apa": {
        "name": "APA (American Psychological Association)",
        "in_text_format": "({authors}, {year})",
        "reference_format": (
            "{authors} ({year}). {title}. {journal}, {volume}({issue}), {pages}. "
            "https://doi.org/{doi}"
        ),
        "order": "alphabetical",
        "max_authors_in_text": 2,
        "et_al_threshold": 3,
        "rules": [
            "List authors alphabetically by last name",
            "Use ampersand (&) before last author in reference list",
            "Use 'et al.' after first author in text for 3+ authors",
            "Italicize journal name and volume",
            "Include DOI when available",
            "Capitalize only first word of article title",
        ],
    },
    "mla": {
        "name": "MLA (Modern Language Association)",
        "in_text_format": "({authors} {page})",
        "reference_format": (
            "{authors}. \"{title}.\" {journal}, vol. {volume}, no. {issue}, "
            "{year}, pp. {pages}."
        ),
        "order": "alphabetical",
        "max_authors_in_text": 2,
        "et_al_threshold": 3,
        "rules": [
            "List authors alphabetically by last name",
            "Use 'et al.' for works with more than 3 authors",
            "Italicize journal name",
            "Use quotation marks around article title",
            "Capitalize all major words in title",
        ],
    },
    "chicago": {
        "name": "Chicago/Turabian",
        "in_text_format": "({authors} {year}, {pages})",
        "reference_format": (
            "{authors}. \"{title}.\" {journal} {volume}, no. {issue} ({year}): {pages}."
        ),
        "order": "alphabetical",
        "max_authors_in_text": 3,
        "et_al_threshold": 4,
        "rules": [
            "Use footnotes or author-date system",
            "Italicize journal name",
            "Use title case for article title",
            "Include issue number for journals",
        ],
    },
    "ieee": {
        "name": "IEEE",
        "in_text_format": "[{index}]",
        "reference_format": (
            "[{index}] {authors}, \"{title},\" {journal}, vol. {volume}, "
            "no. {issue}, pp. {pages}, {year}."
        ),
        "order": "numbered",
        "max_authors_in_text": 6,
        "et_al_threshold": 6,
        "rules": [
            "Number references in order of first appearance",
            "Use square brackets for in-text citations",
            "List all authors up to 6, then use 'et al.'",
            "Abbreviate journal names",
            "Capitalize only first word of title",
        ],
    },
    "harvard": {
        "name": "Harvard",
        "in_text_format": "({authors}, {year})",
        "reference_format": (
            "{authors} ({year}) '{title}', {journal}, {volume}({issue}), "
            "pp. {pages}."
        ),
        "order": "alphabetical",
        "max_authors_in_text": 2,
        "et_al_threshold": 3,
        "rules": [
            "List authors alphabetically",
            "Use 'and' between last two authors",
            "Italicize journal name",
            "Use single quotes around article title",
        ],
    },
    "vancouver": {
        "name": "Vancouver",
        "in_text_format": "{index}",
        "reference_format": (
            "{index}. {authors}. {title}. {journal}. "
            "{year};{volume}({issue}):{pages}."
        ),
        "order": "numbered",
        "max_authors_in_text": 6,
        "et_al_threshold": 6,
        "rules": [
            "Number references in order of first appearance",
            "Use Arabic numerals for in-text citations",
            "List up to 6 authors, then 'et al.'",
            "Abbreviate journal names",
            "No italics for journal names",
        ],
    },
    "ama": {
        "name": "AMA (American Medical Association)",
        "in_text_format": "{index}",
        "reference_format": (
            "{index}. {authors}. {title}. {journal}. "
            "{year};{volume}({issue}):{pages}."
        ),
        "order": "numbered",
        "max_authors_in_text": 6,
        "et_al_threshold": 6,
        "rules": [
            "Number references in order of first appearance",
            "Use superscript numbers in text",
            "List up to 6 authors",
            "Abbreviate journal names",
        ],
    },
    "acs": {
        "name": "ACS (American Chemical Society)",
        "in_text_format": "({index})",
        "reference_format": (
            "{index}; {authors}. {title}. {journal}. "
            "{year}, {volume}, {pages}."
        ),
        "order": "numbered",
        "max_authors_in_text": 5,
        "et_al_threshold": 5,
        "rules": [
            "Use superscript numbers in text (preferred)",
            "Or use parenthetical numbers",
            "List up to 5 authors",
            "Abbreviate journal names",
        ],
    },
    "turabian": {
        "name": "Turabian",
        "in_text_format": "({authors} {year}, {pages})",
        "reference_format": (
            "{authors}. \"{title}.\" {journal} {volume}, no. {issue} "
            "({year}): {pages}."
        ),
        "order": "alphabetical",
        "max_authors_in_text": 3,
        "et_al_threshold": 4,
        "rules": [
            "Based on Chicago style",
            "Use footnotes or author-date",
            "Italicize journal name",
            "Include page numbers for specific references",
        ],
    },
}


def get_citation_style(style_key: str) -> dict:
    return CITATION_STYLES.get(style_key, {})


def list_citation_styles() -> dict:
    return CITATION_STYLES
