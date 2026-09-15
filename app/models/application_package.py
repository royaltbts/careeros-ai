from pydantic import BaseModel
from typing import List, Optional
from app.models.opportunity_status import OpportunityStatus
from app.models.profile_tailor import ProfileTailorOutput
from app.models.tailored_resume import TailoredResume
from app.models.evidence_map import EvidenceMapping


class ApplicationPackage(BaseModel):
    job_id: str
    company: str
    title: str

    # Package identity
    package_version: int = 1
    content_hash: str = ""

    # Workflow state
    status: OpportunityStatus = OpportunityStatus.PENDING_APPROVAL
    application_decision: str

    # Application intelligence
    profile: ProfileTailorOutput
    evidence_map: List[EvidenceMapping]
    resume: TailoredResume

    # Readiness and safety
    claims_safe: bool
    resume_ready: bool
    cover_letter_ready: bool
    outreach_ready: bool

    # Risk controls
    forbidden_claims: List[str]
    critical_gaps: List[str]
    core_gaps: List[str]

    # Human governance
    human_approval_required: bool = True
    approved_by_human: bool = False
    approved_content_hash: Optional[str] = None
    reviewer_notes: Optional[str] = None
