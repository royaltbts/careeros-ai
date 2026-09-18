from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from app.follow_up_store import evaluate_and_persist_follow_up
from app.models.application_record import ApplicationRecord


def make_record(submitted_at):
    return ApplicationRecord(
        job_id="TEST-STORE-001",
        company="Test Company",
        title="Customer Success Manager",
        package_version=1,
        content_hash="test-hash",
        application_status="APPLIED",
        submitted_at=submitted_at,
    )


def test_old_application_follow_up_decision_is_persisted():
    submitted_at = (
        datetime.now(timezone.utc) - timedelta(days=8)
    ).isoformat()

    record = make_record(submitted_at)

    with patch(
        "app.follow_up_store.load_application_record",
        return_value=record,
    ) as load_mock, patch(
        "app.follow_up_store.save_application_record"
    ) as save_mock:

        saved_record, decision = evaluate_and_persist_follow_up(
            "TEST-STORE-001"
        )

    load_mock.assert_called_once_with("TEST-STORE-001")
    save_mock.assert_called_once_with(record)

    assert saved_record is record
    assert decision.follow_up_required is True
    assert decision.action == "REVIEW_OUTREACH"
    assert record.follow_up_required is True
    assert record.follow_up_action == "REVIEW_OUTREACH"
    assert "waiting" in record.follow_up_reason.lower()
    assert record.follow_up_evaluated_at is not None


def test_recent_application_wait_decision_is_persisted():
    submitted_at = (
        datetime.now(timezone.utc) - timedelta(days=2)
    ).isoformat()

    record = make_record(submitted_at)

    with patch(
        "app.follow_up_store.load_application_record",
        return_value=record,
    ), patch(
        "app.follow_up_store.save_application_record"
    ) as save_mock:

        saved_record, decision = evaluate_and_persist_follow_up(
            "TEST-STORE-001"
        )

    save_mock.assert_called_once_with(record)

    assert saved_record is record
    assert decision.follow_up_required is False
    assert decision.action == "WAIT"
    assert record.follow_up_required is False
    assert record.follow_up_action == "WAIT"
    assert record.follow_up_reason is not None
    assert record.follow_up_evaluated_at is not None
