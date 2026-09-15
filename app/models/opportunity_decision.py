from pydantic import BaseModel
from typing import List, Optional


class OpportunityDecision(BaseModel):
    job_id: str
    company: str
    title: str

    opportunity_score: float
    priority: str
    recommendation: str

    decision_reasons: List[str] = []
    strengths: List[str] = []
    critical_gaps: List[str] = []
    transferable_opportunities: List[str] = []

    company_strategic_alignment: Optional[float] = None
    company_research_confidence: Optional[float] = None
    company_research_coverage: Optional[float] = None
    company_research_evidence_confidence: Optional[float] = None
    company_research_quality: Optional[float] = None
    company_decision_ready_fit: Optional[float] = None

    human_review_required: bool = True
