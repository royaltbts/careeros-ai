from app.company_research import (
    CompanyResearchResult,
)
from app.company_research_mapper import (
    map_research_to_intelligence,
)
from app.company_research_validator import (
    validate_research,
)


def process_company_research(
    research: CompanyResearchResult,
):
    is_valid, errors = validate_research(research)

    if not is_valid:
        raise ValueError(
            "Company research validation failed: "
            + " | ".join(errors)
        )

    return map_research_to_intelligence(research)
