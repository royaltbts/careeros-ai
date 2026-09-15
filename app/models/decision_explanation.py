from pydantic import BaseModel, Field


class DecisionEvidenceItem(BaseModel):
    requirement: str
    criticality: str
    category: str
    match_type: str
    confidence: str
    evidence_ids: list[str] = Field(default_factory=list)
    evidence_claims: list[str] = Field(default_factory=list)
    evidence_types: list[str] = Field(default_factory=list)
    allowed: bool
    explanation: str


class DecisionExplanation(BaseModel):
    job_id: str
    company: str
    title: str
    opportunity_score: float
    priority: str
    recommendation: str
    strengths: list[str] = Field(default_factory=list)
    evidence_items: list[DecisionEvidenceItem] = Field(default_factory=list)
    critical_gaps: list[str] = Field(default_factory=list)
    transferable_opportunities: list[str] = Field(default_factory=list)
    confidence_summary: str
    human_review_required: bool = True
