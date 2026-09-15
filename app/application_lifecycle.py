from app.models.application_record import ApplicationRecord
from app.models.application_event import ApplicationEvent
from app.models.opportunity_status import OpportunityStatus
from app.opportunity_workflow import transition_status


def transition_application(
    record: ApplicationRecord,
    new_status: OpportunityStatus,
) -> ApplicationRecord:
    """
    Transition an application CRM record using the canonical
    CareerOS opportunity state machine.

    No external action is performed.
    """

    current_status = OpportunityStatus(
        record.application_status
    )

    transition_status(
        current_status,
        new_status,
    )

    record.application_status = new_status.value

    record.history.append(
        ApplicationEvent.status_change(
            current_status.value,
            new_status.value,
        )
    )

    return record
