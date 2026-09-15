from datetime import datetime, timezone

from app.models.application_record import ApplicationRecord
from app.models.follow_up import FollowUpDecision


DEFAULT_FOLLOW_UP_DAYS = 7


def _days_since(timestamp: str) -> float:
    event_time = datetime.fromisoformat(timestamp)

    return (
        datetime.now(timezone.utc) - event_time
    ).total_seconds() / 86400


def _latest_event(record: ApplicationRecord):
    if not record.history:
        return None

    return max(
        record.history,
        key=lambda event: event.timestamp,
    )


def evaluate_follow_up(
    record: ApplicationRecord,
    threshold_days: int = DEFAULT_FOLLOW_UP_DAYS,
) -> FollowUpDecision:
    """
    Determine whether an application requires follow-up.

    This function makes a recommendation only.
    It performs no external action.
    """

    status = record.application_status

    if status == "APPLIED":
        if not record.submitted_at:
            return FollowUpDecision(
                job_id=record.job_id,
                company=record.company,
                title=record.title,
                current_status=status,
                follow_up_required=False,
                action="WAIT",
                reason="Application has no submission timestamp.",
                priority="NORMAL",
            )

        age_days = _days_since(record.submitted_at)

        if age_days >= threshold_days:
            return FollowUpDecision(
                job_id=record.job_id,
                company=record.company,
                title=record.title,
                current_status=status,
                follow_up_required=True,
                action="REVIEW_OUTREACH",
                reason=(
                    f"Application has been waiting "
                    f"{age_days:.1f} days, exceeding "
                    f"the {threshold_days}-day threshold."
                ),
                days_since_last_event=age_days,
                priority="HIGH",
            )

        return FollowUpDecision(
            job_id=record.job_id,
            company=record.company,
            title=record.title,
            current_status=status,
            follow_up_required=False,
            action="WAIT",
            reason=(
                f"Application is only "
                f"{age_days:.1f} days old."
            ),
            days_since_last_event=age_days,
            priority="NORMAL",
        )

    if status == "INTERVIEW":
        latest_event = _latest_event(record)

        if latest_event is None:
            return FollowUpDecision(
                job_id=record.job_id,
                company=record.company,
                title=record.title,
                current_status=status,
                follow_up_required=False,
                action="REVIEW",
                reason=(
                    "Interview stage has no lifecycle event "
                    "timestamp to evaluate."
                ),
                priority="NORMAL",
            )

        age_days = _days_since(
            latest_event.timestamp
        )

        if (
            latest_event.to_status == "INTERVIEW"
            and age_days >= threshold_days
        ):
            return FollowUpDecision(
                job_id=record.job_id,
                company=record.company,
                title=record.title,
                current_status=status,
                follow_up_required=True,
                action="REVIEW_OUTREACH",
                reason=(
                    f"Interview stage has been waiting "
                    f"{age_days:.1f} days since the latest "
                    f"interview-stage event."
                ),
                days_since_last_event=age_days,
                priority="HIGH",
            )

        return FollowUpDecision(
            job_id=record.job_id,
            company=record.company,
            title=record.title,
            current_status=status,
            follow_up_required=False,
            action="WAIT_FOR_INTERVIEW_OUTCOME",
            reason=(
                f"Interview stage is only "
                f"{age_days:.1f} days old."
            ),
            days_since_last_event=age_days,
            priority="NORMAL",
        )

    if status == "OFFER":
        return FollowUpDecision(
            job_id=record.job_id,
            company=record.company,
            title=record.title,
            current_status=status,
            follow_up_required=False,
            action="WAIT_FOR_DECISION",
            reason=(
                "Offer stage does not require "
                "application follow-up."
            ),
            priority="NORMAL",
        )

    if status == "ACCEPTED":
        return FollowUpDecision(
            job_id=record.job_id,
            company=record.company,
            title=record.title,
            current_status=status,
            follow_up_required=False,
            action="CLOSED",
            reason="Application has been accepted.",
            priority="NORMAL",
        )

    if status == "REJECTED":
        return FollowUpDecision(
            job_id=record.job_id,
            company=record.company,
            title=record.title,
            current_status=status,
            follow_up_required=False,
            action="CLOSED",
            reason="Application was rejected.",
            priority="NORMAL",
        )

    return FollowUpDecision(
        job_id=record.job_id,
        company=record.company,
        title=record.title,
        current_status=status,
        follow_up_required=False,
        action="REVIEW",
        reason=f"No follow-up policy defined for status {status}.",
        priority="NORMAL",
    )
