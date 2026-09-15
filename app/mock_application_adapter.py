from datetime import datetime, timezone

from app.models.application_package import ApplicationPackage
from app.models.execution_authorization import ExecutionAuthorization
from app.models.execution_result import ExecutionResult
from app.execution_authorizer import (
    can_execute_action,
    authorization_block_reason,
)


def submit_application(
    package: ApplicationPackage,
    authorization: ExecutionAuthorization,
) -> ExecutionResult:
    """
    Simulate an application submission.

    IMPORTANT:
    This function performs NO external network action.
    """

    action = "APPLICATION_SUBMISSION"

    if not can_execute_action(
        package,
        authorization,
        action,
    ):
        return ExecutionResult(
            job_id=package.job_id,
            company=package.company,
            title=package.title,
            action=action,
            execution_status="BLOCKED",
            package_version=package.package_version,
            content_hash=package.content_hash,
            executed_at=datetime.now(
                timezone.utc
            ).isoformat(),
            message=authorization_block_reason(
                package,
                authorization,
                action,
            ),
        )

    return ExecutionResult(
        job_id=package.job_id,
        company=package.company,
        title=package.title,
        action=action,
        execution_status="SIMULATED",
        package_version=package.package_version,
        content_hash=package.content_hash,
        executed_at=datetime.now(
            timezone.utc
        ).isoformat(),
        external_reference=(
            f"SIM-{package.job_id}-V"
            f"{package.package_version}"
        ),
        message=(
            "Application submission simulated successfully. "
            "No external system was contacted."
        ),
    )
