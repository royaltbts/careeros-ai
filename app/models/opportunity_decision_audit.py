from datetime import datetime, timezone

from pydantic import BaseModel, Field


class OpportunityDecisionAudit(BaseModel):
    job_id: str
    company: str
    title: str

    opportunity_score: float
    priority: str
    recommendation: str

    decision_reasons: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    critical_gaps: list[str] = Field(default_factory=list)
    transferable_opportunities: list[str] = Field(
        default_factory=list
    )

    company_strategic_alignment: float | None = None
    company_research_confidence: float | None = None
    company_research_coverage: float | None = None
    company_research_evidence_confidence: float | None = None
    company_research_quality: float | None = None
    company_decision_ready_fit: float | None = None

    human_review_required: bool = True

    recorded_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
