from pydantic import BaseModel
from typing import List


class ClaimFidelityCheck(BaseModel):
    claim: str
    evidence_ids: List[str]
    supported_terms: List[str]
    unsupported_terms: List[str]
    unsupported_numbers: List[str]
    unsupported_entities: List[str]
    unsupported_ownership: List[str]
    supported: bool
    reason: str
    human_review_required: bool
