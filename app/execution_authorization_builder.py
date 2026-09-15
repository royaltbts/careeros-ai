from app.models.application_package import ApplicationPackage
from app.models.execution_authorization import ExecutionAuthorization


def build_execution_authorization(
    package: ApplicationPackage,
) -> ExecutionAuthorization:
    """
    Create a PENDING execution authorization tied to the
    exact approved application package.

    This function does not authorize any external action.
    Human authorization must happen separately.
    """

    return ExecutionAuthorization(
        job_id=package.job_id,
        company=package.company,
        title=package.title,
        package_version=package.package_version,
        approved_content_hash=package.content_hash,
        approved_by_human=False,
        application_submission_authorized=False,
        outreach_authorized=False,
        authorization_status="PENDING",
        authorized_at=None,
        reviewer_notes=None,
    )
