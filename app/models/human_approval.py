from pydantic import BaseModel
from typing import Optional


class HumanApproval(BaseModel):
    job_id: str
    company: str
    title: str

    resume_ready: bool
    cover_letter_ready: bool
    outreach_ready: bool

    claims_safe: bool

    decision: str = "PENDING"

    reviewer_notes: Optional[str] = None

    approved_by_human: bool = False
