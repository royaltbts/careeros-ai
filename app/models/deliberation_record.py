from datetime import datetime, timezone

from pydantic import BaseModel, Field


class DeliberationRecord(BaseModel):
    job_id: str
    company: str
    title: str

    cycle_id: str

    agent_findings: list[dict] = Field(
        default_factory=list
    )

    disagreements: list[dict] = Field(
        default_factory=list
    )

    supervisor_recommendation: str
    supervisor_confidence: float

    supervisor_conflicts: list[str] = Field(
        default_factory=list
    )

    unresolved_questions: list[str] = Field(
        default_factory=list
    )

    human_review_required: bool = True
    external_action_allowed: bool = False

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
