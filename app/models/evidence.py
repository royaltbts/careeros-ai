from pydantic import BaseModel
from typing import List


class EvidenceItem(BaseModel):
    id: str

    capability: str

    claim: str

    evidence: str

    source: str

    evidence_type: str

    status: str

    allowed_use: List[str]
