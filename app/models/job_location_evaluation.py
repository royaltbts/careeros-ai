from pydantic import BaseModel


class JobLocationEvaluation(BaseModel):
    eligible: bool
    reason: str
    confidence: float
    verification_required: bool = False
