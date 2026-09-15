from pydantic import BaseModel
from typing import Optional

from app.models.outreach_message import OutreachMessage
from app.models.follow_up_recommendation import FollowUpRecommendation


class OutreachReview(BaseModel):
    job_id: str
    company: str
    title: str

    recommendation: FollowUpRecommendation
    message: OutreachMessage

    package_version: int = 1
    content_hash: str = ""

    decision: str = "PENDING"
    approved_by_human: bool = False
    approved_content_hash: Optional[str] = None

    reviewer_notes: Optional[str] = None
