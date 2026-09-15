from pydantic import BaseModel


class FollowUpDecision(BaseModel):
    job_id: str
    company: str
    title: str

    current_status: str
    follow_up_required: bool

    action: str
    reason: str

    days_since_last_event: float | None = None
    next_review_at: str | None = None
    priority: str = "NORMAL"

    human_approval_required: bool = True
