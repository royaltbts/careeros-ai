from pydantic import BaseModel, Field


class CandidateFinding(BaseModel):
    agent: str = "Candidate Profile Analyst"

    strengths: list[str] = Field(
        default_factory=list
    )

    transferable_experience: list[str] = Field(
        default_factory=list
    )

    verified_evidence_refs: list[str] = Field(
        default_factory=list
    )

    explicit_gaps: list[str] = Field(
        default_factory=list
    )

    forbidden_assumptions: list[str] = Field(
        default_factory=list
    )

    recommendation: str = "APPLY"

    confidence: float = 0.0
