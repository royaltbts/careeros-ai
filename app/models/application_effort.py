from pydantic import BaseModel


class ApplicationEffort(BaseModel):
    job_id: str
    company: str
    title: str
    recommendation: str
    opportunity_score: float
    effort_level: str
    effort_reason: str
    recommended_actions: list[str]
