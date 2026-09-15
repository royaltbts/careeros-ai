from typing import List

from pydantic import BaseModel

from app.models.company_intelligence import (
    CompanyFact,
    CompanyIntelligence,
)


class CompanyResearchResult(BaseModel):
    """
    Raw research returned by an external research source.

    This layer does not assume that any fact is true.
    Facts must carry their source and confidence.
    """

    company: str
    facts: List[CompanyFact]
    research_status: str = "WEB_RESEARCHED"


def build_researched_intelligence(
    research: CompanyResearchResult,
) -> CompanyIntelligence:
    """
    Convert source-backed research into structured
    Company Intelligence.

    No company facts are invented here.
    """

    intelligence = CompanyIntelligence(
        company=research.company,
        facts=research.facts,
        research_status=research.research_status,
        human_review_required=True,
    )

    return intelligence
