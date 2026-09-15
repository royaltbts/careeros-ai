from pydantic import BaseModel
from typing import List, Optional


class JobRequirement(BaseModel):
    name: str
    criticality: str
    category: str


class Job(BaseModel):
    job_id: str
    company: str
    title: str
    location: Optional[str] = None
    employment_type: Optional[str] = None

    description: str

    responsibilities: List[str]

    requirements: List[JobRequirement]

    experience_required: Optional[str] = None
    industry: Optional[str] = None

    source_url: Optional[str] = None
