from pydantic import BaseModel
from typing import List, Optional

from app.models.job import JobRequirement


class JobIntelligence(BaseModel):
    job_id: str
    company: str
    title: str
    location: Optional[str] = None
    employment_type: Optional[str] = None
    industry: Optional[str] = None
    experience_required: Optional[str] = None

    responsibilities: List[str]
    requirements: List[JobRequirement]

    customer_success_capabilities: List[str]
    tools_and_platforms: List[str]

    source_url: Optional[str] = None
    source_type: Optional[str] = None
