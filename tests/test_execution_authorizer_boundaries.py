import copy

from app.careeros import load_existing_application_package
from app.execution_authorizer import (
    can_execute_action,
    authorization_block_reason,
)
from app.models.execution_authorization import ExecutionAuthorization
from app.models.opportunity_status import OpportunityStatus
from app.package_integrity import calculate_content_hash


def approved_package():
    package = load_existing_application_package("JOB-001")
    assert package is not None
    package = copy.deepcopy(package)
    package.status = OpportunityStatus.APPROVED
    package.approved_by_human = True
    package.content_hash = calculate_content_hash(package)
    package.approved_content_hash = package.content_hash
    return package


def authorization_for(package):
    return ExecutionAuthorization(
        job_id=package.job_id,
        company=package.company,
        title=package.title,
        package_version=package.package_version,
        approved_content_hash=package.content_hash,
    )


def test_wrong_job_id_blocks_application_submission():
    package = approved_package()
    authorization = authorization_for(package)
    authorization.authorize(application_submission=True)
    authorization.job_id = "OTHER-JOB"

    assert not can_execute_action(
        package,
        authorization,
        "APPLICATION_SUBMISSION",
    )
    assert "job does not match" in authorization_block_reason(
        package,
        authorization,
        "APPLICATION_SUBMISSION",
    )


def test_revoked_human_approval_blocks_application_submission():
    package = approved_package()
    authorization = authorization_for(package)
    authorization.authorize(application_submission=True)
    authorization.approved_by_human = False

    assert not can_execute_action(
        package,
        authorization,
        "APPLICATION_SUBMISSION",
    )
    assert "not explicitly approved" in authorization_block_reason(
        package,
        authorization,
        "APPLICATION_SUBMISSION",
    )
