import pytest

from app.application_lifecycle import transition_application
from app.models.application_event import ApplicationEvent
from app.models.application_record import ApplicationRecord
from app.models.opportunity_status import OpportunityStatus


def make_record(status="APPROVED"):
    return ApplicationRecord(
        job_id="TEST-LIFECYCLE-001",
        company="Test Company",
        title="Customer Success Manager",
        package_version=1,
        content_hash="test-hash",
        application_status=status,
    )


def test_valid_transition_updates_status_and_appends_event():
    record = make_record("APPROVED")

    result = transition_application(
        record,
        OpportunityStatus.APPLIED,
    )

    assert result is record
    assert result.application_status == "APPLIED"
    assert len(result.history) == 1

    event = result.history[0]
    assert isinstance(event, ApplicationEvent)
    assert event.event_type == "STATUS_CHANGE"
    assert event.from_status == "APPROVED"
    assert event.to_status == "APPLIED"


def test_invalid_transition_raises_and_does_not_change_record():
    record = make_record("APPROVED")

    with pytest.raises(ValueError, match="Invalid opportunity transition"):
        transition_application(
            record,
            OpportunityStatus.INTERVIEW,
        )

    assert record.application_status == "APPROVED"
    assert record.history == []


def test_transition_to_applied_does_not_create_submission_metadata():
    record = make_record("APPROVED")

    result = transition_application(record, OpportunityStatus.APPLIED)

    assert result.submitted_at is None
    assert result.external_reference is None
