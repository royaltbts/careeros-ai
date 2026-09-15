from app.models.application_record import ApplicationRecord
from app.models.execution_result import ExecutionResult


def create_application_record(
    result: ExecutionResult,
) -> ApplicationRecord:
    """
    Convert an execution result into an Application CRM record.

    Only successful or simulated application submissions
    become APPLIED records.
    """

    record = ApplicationRecord(
        job_id=result.job_id,
        company=result.company,
        title=result.title,
        package_version=result.package_version,
        content_hash=result.content_hash,
        source="CAREEROS",
        notes=result.message,
    )

    if result.execution_status in {
        "SIMULATED",
        "SUCCESS",
    }:
        record.mark_submitted(
            external_reference=result.external_reference,
            notes=result.message,
        )

    return record
