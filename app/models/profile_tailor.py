from pydantic import BaseModel
from typing import List


class TailoredClaim(BaseModel):
    requirement: str
    suggested_claim: str
    evidence_id: str
    evidence_type: str
    confidence: str
    allowed: bool


class ProfileTailorOutput(BaseModel):
    job_id: str
    company: str
    title: str

    positioning_statement: str

    matched_claims: List[TailoredClaim]
    transferable_claims: List[TailoredClaim]

    missing_requirements: List[str]
    forbidden_claims: List[str]

    human_review_required: bool
