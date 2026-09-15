from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel


class ExecutionAuthorization(BaseModel):
    job_id: str
    company: str
    title: str

    package_version: int
    approved_content_hash: str

    approved_by_human: bool = False

    application_submission_authorized: bool = False
    outreach_authorized: bool = False

    authorization_status: str = "PENDING"

    authorized_at: Optional[str] = None
    reviewer_notes: Optional[str] = None

    def authorize(
        self,
        application_submission: bool = False,
        outreach: bool = False,
        reviewer_notes: Optional[str] = None,
    ) -> None:
        self.application_submission_authorized = (
            application_submission
        )
        self.outreach_authorized = outreach
        self.approved_by_human = True
        self.authorization_status = "AUTHORIZED"
        self.authorized_at = datetime.now(
            timezone.utc
        ).isoformat()
        self.reviewer_notes = reviewer_notes
