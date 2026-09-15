from pydantic import BaseModel, Field


class AgentFinding(BaseModel):
    agent: str
    finding: str
    confidence: float
    evidence_refs: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    recommendation: str | None = None


class AgentDisagreement(BaseModel):
    agents: list[str]
    topic: str
    positions: list[str]
    resolution_required: bool = True


class SupervisorCase(BaseModel):
    job_id: str
    company: str
    title: str

    findings: list[AgentFinding] = Field(
        default_factory=list
    )

    disagreements: list[AgentDisagreement] = Field(
        default_factory=list
    )

    unresolved_questions: list[str] = Field(
        default_factory=list
    )

    human_review_required: bool = True
