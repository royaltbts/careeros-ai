from typing import Optional

from pydantic import BaseModel


class EvidenceMatch(BaseModel):
    requirement: str
    evidence_id: str
    match_type: str
    score: float
    rationale: str
    suggested_use: Optional[str] = None
