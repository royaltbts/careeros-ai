import json
from pathlib import Path

from app.application_crm import create_application_record
from app.application_crm_store import save_application_record
from app.execution_authorizer import (
    can_execute_action,
    authorization_block_reason,
)
from app.models.application_package import ApplicationPackage
from app.models.execution_authorization import ExecutionAuthorization
from app.models.execution_result import ExecutionResult
from app.models.opportunity_status import OpportunityStatus
from app.opportunity_workflow import transition_status


PACKAGE_DIR = Path("data/jobs/applications")


def execute_application(
    package: ApplicationPackage,
    authorization: ExecutionAuthorization,
    adapter,
) -> ExecutionResult:
    """
    Execute an application through an injected adapter.

    The adapter may be a mock adapter or, later, a real ATS adapter.

    The service itself does not perform external network operations.
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
            executed_at="",
            message=authorization_block_reason(
                package,
                authorization,
                action,
            ),
        )

    result = adapter.submit_application(
        package,
        authorization,
    )

    if result.execution_status in {
        "SIMULATED",
        "SUCCESS",
    }:
        new_status = transition_status(
            package.status,
            OpportunityStatus.APPLIED,
        )

        package.status = new_status

        package_path = (
            PACKAGE_DIR / f"{package.job_id}.json"
        )

        with open(package_path, "w") as f:
            json.dump(
                package.model_dump(mode="json"),
                f,
                indent=2,
            )

        record = create_application_record(result)
        save_application_record(record)

    return result
