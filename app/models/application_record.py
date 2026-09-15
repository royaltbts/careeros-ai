from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel

from app.models.application_event import ApplicationEvent


class ApplicationRecord(BaseModel):
    job_id: str
    company: str
    title: str

    package_version: int
    content_hash: str

    application_status: str = "NOT_APPLIED"

    submitted_at: Optional[str] = None
    external_reference: Optional[str] = None

    source: str = "CAREEROS"
    notes: Optional[str] = None

    last_updated: str = ""
    history: list[ApplicationEvent] = []

    follow_up_required: bool = False
    follow_up_action: Optional[str] = None
    follow_up_reason: Optional[str] = None
    follow_up_evaluated_at: Optional[str] = None

    def mark_submitted(
        self,
        external_reference: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> None:
        self.application_status = "APPLIED"
        self.submitted_at = datetime.now(
            timezone.utc
        ).isoformat()
        self.external_reference = external_reference
        self.notes = notes
        self.last_updated = datetime.now(
            timezone.utc
        ).isoformat()
