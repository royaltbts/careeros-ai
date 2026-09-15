from urllib.parse import urlparse

from app.company_research import CompanyResearchResult


VALID_CONFIDENCE = {
    "HIGH",
    "MEDIUM",
    "LOW",
}


def validate_research(
    research: CompanyResearchResult,
) -> tuple[bool, list[str]]:

    errors = []

    if (
        research.research_status == "WEB_RESEARCHED"
        and not research.facts
    ):
        errors.append(
            "WEB_RESEARCHED research requires at least one fact."
        )

    if not research.company.strip():
        errors.append("Company name is missing.")

    for index, fact in enumerate(research.facts, start=1):

        if not fact.fact.strip():
            errors.append(
                f"Fact {index}: fact text is missing."
            )

        if not fact.source.strip():
            errors.append(
                f"Fact {index}: source is missing."
            )
        elif research.research_status == "WEB_RESEARCHED":
            parsed_source = urlparse(
                fact.source.strip()
            )
            if parsed_source.scheme not in {
                "http",
                "https",
            } or not parsed_source.netloc:
                errors.append(
                    f"Fact {index}: source must be a valid "
                    "HTTP/HTTPS URL."
                )

        if fact.confidence.upper() not in VALID_CONFIDENCE:
            errors.append(
                f"Fact {index}: invalid confidence "
                f"'{fact.confidence}'."
            )

        if not fact.category.strip():
            errors.append(
                f"Fact {index}: category is missing."
            )

    return len(errors) == 0, errors
