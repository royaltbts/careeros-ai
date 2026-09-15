from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel


class OutreachAuthorization(BaseModel):
    job_id: str
    company: str
    title: str

    recommendation: str
    package_version: int
    content_hash: str

    approved_by_human: bool = False
    outreach_authorized: bool = False

    authorization_status: str = "PENDING"
    authorized_at: Optional[str] = None
    reviewer_notes: Optional[str] = None

    def authorize(self, reviewer_notes: Optional[str] = None):
        self.approved_by_human = True
        self.outreach_authorized = True
        self.authorization_status = "AUTHORIZED"
        self.authorized_at = datetime.now(
            timezone.utc
        ).isoformat()
        self.reviewer_notes = reviewer_notes
