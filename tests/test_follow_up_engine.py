from datetime import datetime, timedelta, timezone

from app.follow_up_engine import evaluate_follow_up
from app.models.application_event import ApplicationEvent
from app.models.application_record import ApplicationRecord


def make_record(
    status="APPLIED",
    submitted_at=None,
    history=None,
):
    return ApplicationRecord(
        job_id="TEST-FOLLOW-001",
        company="Test Company",
        title="Customer Success Manager",
        package_version=1,
        content_hash="test-hash",
        application_status=status,
        submitted_at=submitted_at,
        history=history or [],
    )


def test_recent_applied_application_should_wait():
    submitted_at = (
        datetime.now(timezone.utc) - timedelta(days=3)
    ).isoformat()

    decision = evaluate_follow_up(
        make_record(submitted_at=submitted_at)
    )

    assert decision.follow_up_required is False
    assert decision.action == "WAIT"
    assert decision.priority == "NORMAL"


def test_old_applied_application_requires_follow_up():
    submitted_at = (
        datetime.now(timezone.utc) - timedelta(days=8)
    ).isoformat()

    decision = evaluate_follow_up(
        make_record(submitted_at=submitted_at)
    )

    assert decision.follow_up_required is True
    assert decision.action == "REVIEW_OUTREACH"
    assert decision.priority == "HIGH"


def test_applied_without_submission_timestamp_should_wait():
    decision = evaluate_follow_up(
        make_record(submitted_at=None)
    )

    assert decision.follow_up_required is False
    assert decision.action == "WAIT"


def test_old_interview_stage_requires_follow_up():
    timestamp = (
        datetime.now(timezone.utc) - timedelta(days=8)
    ).isoformat()

    event = ApplicationEvent(
        event_type="STATUS_CHANGE",
        from_status="APPLIED",
        to_status="INTERVIEW",
        timestamp=timestamp,
    )

    decision = evaluate_follow_up(
        make_record(
            status="INTERVIEW",
            history=[event],
        )
    )

    assert decision.follow_up_required is True
    assert decision.action == "REVIEW_OUTREACH"
    assert decision.priority == "HIGH"


def test_recent_interview_stage_should_wait_for_outcome():
    timestamp = (
        datetime.now(timezone.utc) - timedelta(days=3)
    ).isoformat()

    event = ApplicationEvent(
        event_type="STATUS_CHANGE",
        from_status="APPLIED",
        to_status="INTERVIEW",
        timestamp=timestamp,
    )

    decision = evaluate_follow_up(
        make_record(
            status="INTERVIEW",
            history=[event],
        )
    )

    assert decision.follow_up_required is False
    assert decision.action == "WAIT_FOR_INTERVIEW_OUTCOME"


def test_interview_without_history_requires_review():
    decision = evaluate_follow_up(
        make_record(
            status="INTERVIEW",
            history=[],
        )
    )

    assert decision.follow_up_required is False
    assert decision.action == "REVIEW"


def test_offer_should_not_require_follow_up():
    decision = evaluate_follow_up(
        make_record(status="OFFER")
    )

    assert decision.follow_up_required is False
    assert decision.action == "WAIT_FOR_DECISION"


def test_accepted_application_should_be_closed():
    decision = evaluate_follow_up(
        make_record(status="ACCEPTED")
    )

    assert decision.follow_up_required is False
    assert decision.action == "CLOSED"


def test_rejected_application_should_be_closed():
    decision = evaluate_follow_up(
        make_record(status="REJECTED")
    )

    assert decision.follow_up_required is False
    assert decision.action == "CLOSED"


def test_unknown_status_should_return_review():
    decision = evaluate_follow_up(
        make_record(status="NOT_APPLIED")
    )

    assert decision.follow_up_required is False
    assert decision.action == "REVIEW"
