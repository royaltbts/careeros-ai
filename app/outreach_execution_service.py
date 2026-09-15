from app.models.outreach_authorization import OutreachAuthorization
from app.models.outreach_execution_result import OutreachExecutionResult
from app.models.outreach_message import OutreachMessage
from app.outreach_authorizer import (
    can_execute_outreach,
    outreach_block_reason,
)


def execute_outreach(
    message: OutreachMessage,
    authorization: OutreachAuthorization,
    adapter,
) -> OutreachExecutionResult:
    """
    Execute an outreach action through an injected adapter.

    The service performs no external network operation itself.
    Authorization is checked before the adapter is called.
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
            executed_at="",
            message=outreach_block_reason(
                message,
                authorization,
            ),
        )

    return adapter.send_outreach(
        message,
        authorization,
    )
