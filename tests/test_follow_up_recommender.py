from datetime import datetime, timedelta, timezone

from app.follow_up_recommender import create_follow_up_recommendation
from app.models.application_event import ApplicationEvent
from app.models.application_record import ApplicationRecord


def make_record(
    status="APPLIED",
    submitted_at=None,
    history=None,
):
    return ApplicationRecord(
        job_id="TEST-RECOMMENDER-001",
        company="Test Company",
        title="Customer Success Manager",
        package_version=1,
        content_hash="test-hash",
        application_status=status,
        submitted_at=submitted_at,
        history=history or [],
    )


def test_recent_application_becomes_wait_recommendation():
    submitted_at = (
        datetime.now(timezone.utc) - timedelta(days=2)
    ).isoformat()

    recommendation = create_follow_up_recommendation(
        make_record(submitted_at=submitted_at)
    )

    assert recommendation.recommendation == "WAIT"
    assert recommendation.priority == "NORMAL"
    assert recommendation.current_status == "APPLIED"
    assert recommendation.human_review_required is True


def test_old_application_becomes_outreach_recommendation():
    submitted_at = (
        datetime.now(timezone.utc) - timedelta(days=8)
    ).isoformat()

    recommendation = create_follow_up_recommendation(
        make_record(submitted_at=submitted_at)
    )

    assert recommendation.recommendation == "REVIEW_OUTREACH"
    assert recommendation.priority == "HIGH"
    assert recommendation.days_since_last_event >= 7


def test_latest_event_type_is_preserved():
    old_timestamp = (
        datetime.now(timezone.utc) - timedelta(days=10)
    ).isoformat()
    recent_timestamp = (
        datetime.now(timezone.utc) - timedelta(days=2)
    ).isoformat()

    events = [
        ApplicationEvent(
            event_type="STATUS_CHANGE",
            from_status="APPLIED",
            to_status="INTERVIEW",
            timestamp=old_timestamp,
        ),
        ApplicationEvent(
            event_type="INTERVIEW_COMPLETED",
            timestamp=recent_timestamp,
        ),
    ]

    recommendation = create_follow_up_recommendation(
        make_record(
            status="INTERVIEW",
            history=events,
        )
    )

    assert recommendation.triggering_event_type == "INTERVIEW_COMPLETED"
    assert recommendation.recommendation == "WAIT_FOR_INTERVIEW_OUTCOME"


def test_no_history_has_no_triggering_event():
    recommendation = create_follow_up_recommendation(
        make_record(status="INTERVIEW")
    )

    assert recommendation.triggering_event_type is None
    assert recommendation.recommendation == "REVIEW"
    assert recommendation.human_review_required is True
