from pydantic import BaseModel
from typing import Optional


class JobDiscovery(BaseModel):
    job_id: str
    company: str
    title: str
    location: Optional[str] = None
    source: str
    source_url: Optional[str] = None
    discovered_at: str
    raw_description: str
