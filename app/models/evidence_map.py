from pydantic import BaseModel
from typing import List


class EvidenceMapping(BaseModel):
    requirement: str
    evidence_ids: List[str]
    match_type: str
    confidence: str
    source: List[str]
    suggested_claim: str
    allowed: bool
    human_review_required: bool
