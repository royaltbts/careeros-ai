from pydantic import BaseModel
from typing import List


class OutreachMessage(BaseModel):
    package_version: int = 1
    job_id: str
    company: str
    title: str

    channel: str
    subject: str
    body: str

    evidence_ids: List[str]

    claims_safe: bool = False
    safety_reason: str = ""

    human_review_required: bool = True
    approved_by_human: bool = False
