from app.application_crm import create_application_record
from app.models.execution_result import ExecutionResult


def make_result(status, external_reference="EXT-123"):
    return ExecutionResult(
        job_id="JOB-CRM-001",
        company="Test Company",
        title="Customer Success Manager",
        action="APPLICATION_SUBMISSION",
        execution_status=status,
        package_version=1,
        content_hash="hash-123",
        executed_at="2026-09-18T12:00:00+00:00",
        external_reference=external_reference,
        message="Application processed.",
    )


def test_simulated_submission_creates_applied_record():
    result = make_result("SIMULATED")

    record = create_application_record(result)

    assert record.application_status == "APPLIED"
    assert record.submitted_at is not None
    assert record.external_reference == "EXT-123"
    assert record.notes == "Application processed."
    assert record.source == "CAREEROS"


def test_success_submission_creates_applied_record():
    result = make_result("SUCCESS", "SUCCESS-REF")

    record = create_application_record(result)

    assert record.application_status == "APPLIED"
    assert record.submitted_at is not None
    assert record.external_reference == "SUCCESS-REF"


def test_blocked_execution_does_not_mark_record_submitted():
    result = make_result("BLOCKED")

    record = create_application_record(result)

    assert record.application_status == "NOT_APPLIED"
    assert record.submitted_at is None
    assert record.external_reference is None
    assert record.notes == "Application processed."
