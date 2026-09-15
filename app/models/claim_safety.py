from pydantic import BaseModel
from typing import List


class ClaimCheck(BaseModel):
    claim: str
    evidence_ids: List[str]
    evidence_verified: bool
    forbidden_match: bool
    fidelity_supported: bool
    fidelity_reason: str
    allowed: bool
    reason: str
    human_review_required: bool

class ClaimSafetyResult(BaseModel):
    job_id: str
    total_claims: int
    approved_claims: int
    blocked_claims: int
    checks: List[ClaimCheck]
    all_claims_safe: bool
    human_review_required: bool
