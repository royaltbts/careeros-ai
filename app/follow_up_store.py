from datetime import datetime, timezone

from app.application_crm_store import (
    load_application_record,
    save_application_record,
)
from app.follow_up_engine import evaluate_follow_up


def evaluate_and_persist_follow_up(
    job_id: str,
    threshold_days: int = 7,
):
    """
    Evaluate follow-up status and persist the decision
    to the application's CRM record.

    No external action is performed.
    """

    record = load_application_record(job_id)

    decision = evaluate_follow_up(
        record,
        threshold_days,
    )

    record.follow_up_required = (
        decision.follow_up_required
    )

    record.follow_up_action = decision.action

    record.follow_up_reason = decision.reason

    record.follow_up_evaluated_at = (
        datetime.now(timezone.utc).isoformat()
    )

    save_application_record(record)

    return record, decision
