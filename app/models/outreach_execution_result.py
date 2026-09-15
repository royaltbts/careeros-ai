from typing import Optional

from pydantic import BaseModel


class OutreachExecutionResult(BaseModel):
    job_id: str
    company: str
    title: str
    channel: str
    action: str
    execution_status: str
    package_version: int
    content_hash: str
    executed_at: str
    external_reference: Optional[str] = None
    message: str = ""
