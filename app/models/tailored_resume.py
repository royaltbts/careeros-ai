from pydantic import BaseModel
from typing import List


class ResumeBullet(BaseModel):
    requirement: str
    bullet: str
    evidence_ids: List[str]
    confidence: str
    allowed: bool
    human_review_required: bool


class TailoredResume(BaseModel):
    job_id: str
    company: str
    title: str
    headline: str
    summary: str
    bullets: List[ResumeBullet]
    excluded_claims: List[str]
    human_review_required: bool
