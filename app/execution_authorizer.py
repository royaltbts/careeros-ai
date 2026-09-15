from app.models.application_package import ApplicationPackage
from app.models.execution_authorization import ExecutionAuthorization
from app.execution_gate import can_execute


def can_execute_action(
    package: ApplicationPackage,
    authorization: ExecutionAuthorization,
    action: str,
) -> bool:
    """
    Verify that a specific external action is explicitly authorized.

    This function performs no external action.
    """

    if not can_execute(package):
        return False

    if authorization.authorization_status != "AUTHORIZED":
        return False

    if not authorization.approved_by_human:
        return False

    if authorization.job_id != package.job_id:
        return False

    if authorization.package_version != package.package_version:
        return False

    if authorization.approved_content_hash != package.content_hash:
        return False

    if action == "APPLICATION_SUBMISSION":
        return authorization.application_submission_authorized

    if action == "OUTREACH":
        return authorization.outreach_authorized

    return False


def authorization_block_reason(
    package: ApplicationPackage,
    authorization: ExecutionAuthorization,
    action: str,
) -> str:
    """
    Explain why a requested external action is blocked.
    """

    if not can_execute(package):
        return "Execution Gate rejected the application package."

    if authorization.authorization_status != "AUTHORIZED":
        return "Execution authorization is not active."

    if not authorization.approved_by_human:
        return "Authorization was not explicitly approved by a human."

    if authorization.job_id != package.job_id:
        return "Authorization job does not match the application package."

    if authorization.package_version != package.package_version:
        return "Authorization package version does not match."

    if authorization.approved_content_hash != package.content_hash:
        return "Authorization hash does not match the approved package."

    if action == "APPLICATION_SUBMISSION":
        if not authorization.application_submission_authorized:
            return "Application submission was not authorized."
        return "Application submission is authorized."

    if action == "OUTREACH":
        if not authorization.outreach_authorized:
            return "Outreach was not authorized."
        return "Outreach is authorized."

    return f"Unknown execution action: {action}"
