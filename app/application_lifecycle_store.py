from app.application_crm_store import (
    load_application_record,
    save_application_record,
)
from app.application_lifecycle import transition_application
from app.models.opportunity_status import OpportunityStatus


def update_application_status(
    job_id: str,
    new_status: OpportunityStatus,
):
    """
    Load, validate, transition, and persist an application status.
    """

    record = load_application_record(job_id)

    transition_application(
        record,
        new_status,
    )

    save_application_record(record)

    return record
