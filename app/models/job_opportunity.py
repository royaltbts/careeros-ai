from pydantic import BaseModel
from typing import Optional

from app.models.opportunity_status import OpportunityStatus


class JobOpportunity(BaseModel):
    job_id: str

    company: str

    title: str

    location: Optional[str] = None

    source: str

    source_url: Optional[str] = None

    discovered_at: str

    status: OpportunityStatus = OpportunityStatus.NEW

    fit_score: Optional[float] = None

    opportunity_score: Optional[float] = None

    priority: Optional[str] = None

    application_decision: Optional[str] = None

    human_approval: bool = False

    notes: Optional[str] = None
