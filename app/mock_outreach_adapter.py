from datetime import datetime, timezone

from app.models.outreach_authorization import OutreachAuthorization
from app.models.outreach_execution_result import OutreachExecutionResult
from app.models.outreach_message import OutreachMessage
from app.outreach_authorizer import (
    can_execute_outreach,
    outreach_block_reason,
)


def send_outreach(
    message: OutreachMessage,
    authorization: OutreachAuthorization,
) -> OutreachExecutionResult:
    """
    Simulate an outreach action.

    IMPORTANT:
    This function performs NO external network action.
    """

    action = "OUTREACH"

    if not can_execute_outreach(
        message,
        authorization,
    ):
        return OutreachExecutionResult(
            job_id=message.job_id,
            company=message.company,
            title=message.title,
            channel=message.channel,
            action=action,
            execution_status="BLOCKED",
            package_version=message.package_version,
            content_hash="",
            executed_at=datetime.now(
                timezone.utc
            ).isoformat(),
            message=outreach_block_reason(
                message,
                authorization,
            ),
        )

    return OutreachExecutionResult(
        job_id=message.job_id,
        company=message.company,
        title=message.title,
        channel=message.channel,
        action=action,
        execution_status="SIMULATED",
        package_version=message.package_version,
        content_hash=(
            __import__(
                "app.outreach_integrity",
                fromlist=["calculate_outreach_hash"],
            ).calculate_outreach_hash(message)
        ),
        executed_at=datetime.now(
            timezone.utc
        ).isoformat(),
        external_reference=(
            f"SIM-OUTREACH-{message.job_id}-V"
            f"{message.package_version}"
        ),
        message=(
            "Outreach simulated successfully. "
            "No external system was contacted."
        ),
    )
