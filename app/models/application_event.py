from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel


class ApplicationEvent(BaseModel):
    event_type: str
    from_status: Optional[str] = None
    to_status: Optional[str] = None
    timestamp: str
    notes: Optional[str] = None

    @classmethod
    def status_change(
        cls,
        from_status: str,
        to_status: str,
        notes: Optional[str] = None,
    ):
        return cls(
            event_type="STATUS_CHANGE",
            from_status=from_status,
            to_status=to_status,
            timestamp=datetime.now(
                timezone.utc
            ).isoformat(),
            notes=notes,
        )
