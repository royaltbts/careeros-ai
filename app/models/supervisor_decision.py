from pydantic import BaseModel, Field


class SupervisorFinding(BaseModel):
    source: str
    finding: str
    confidence: float
    evidence_refs: list[str] = Field(default_factory=list)


class SupervisorDecision(BaseModel):
    job_id: str
    company: str
    title: str

    recommendation: str

    confidence: float

    findings: list[SupervisorFinding] = Field(
        default_factory=list
    )

    conflicts: list[str] = Field(
        default_factory=list
    )

    unresolved_questions: list[str] = Field(
        default_factory=list
    )

    human_review_required: bool = True

    external_action_allowed: bool = False
