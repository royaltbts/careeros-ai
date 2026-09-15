from pydantic import BaseModel
from typing import List


class ApplicationStrategy(BaseModel):
    job_id: str
    company: str
    title: str

    priority: str
    fit_score: float
    opportunity_score: float

    application_decision: str

    resume_tailoring: str
    cover_letter: str
    networking: str

    evidence_strengths: List[str]
    transferable_capabilities: List[str]
    critical_gaps: List[str]
    core_gaps: List[str]

    forbidden_claims: List[str]

    company_strategic_fit: str = ""
    company_risks: List[str] = []
    company_research_status: str = "NOT_RESEARCHED"
    company_intelligence_review_required: bool = True

    human_approval_required: bool
