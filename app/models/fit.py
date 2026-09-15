from pydantic import BaseModel
from typing import List


class FitDimension(BaseModel):
    name: str
    weight: float
    score: float
    rationale: str


class FitResult(BaseModel):
    job_id: str
    company: str
    title: str

    overall_score: float

    dimensions: List[FitDimension]

    strengths: List[str]
    gaps: List[str]
    transferable_matches: List[str]
    risks: List[str]

    recommendation: str
