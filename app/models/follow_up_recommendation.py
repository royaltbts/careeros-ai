from pydantic import BaseModel
from typing import Optional


class FollowUpRecommendation(BaseModel):
    job_id: str
    company: str
    title: str

    current_status: str

    recommendation: str
    priority: str
    reason: str

    days_since_last_event: Optional[float] = None
    triggering_event_type: Optional[str] = None

    human_review_required: bool = True
