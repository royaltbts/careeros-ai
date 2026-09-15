from app.follow_up_engine import evaluate_follow_up
from app.models.application_record import ApplicationRecord
from app.models.follow_up_recommendation import (
    FollowUpRecommendation,
)


def create_follow_up_recommendation(
    record: ApplicationRecord,
    threshold_days: int = 7,
) -> FollowUpRecommendation:
    """
    Convert a follow-up decision into a governed
    follow-up recommendation.

    No external action is performed.
    """

    decision = evaluate_follow_up(
        record,
        threshold_days,
    )

    triggering_event_type = None

    if record.history:
        latest_event = max(
            record.history,
            key=lambda event: event.timestamp,
        )
        triggering_event_type = latest_event.event_type

    return FollowUpRecommendation(
        job_id=decision.job_id,
        company=decision.company,
        title=decision.title,
        current_status=decision.current_status,
        recommendation=decision.action,
        priority=decision.priority,
        reason=decision.reason,
        days_since_last_event=(
            decision.days_since_last_event
        ),
        triggering_event_type=triggering_event_type,
        human_review_required=(
            decision.human_approval_required
        ),
    )
