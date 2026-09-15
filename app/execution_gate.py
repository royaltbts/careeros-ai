from app.models.application_package import ApplicationPackage
from app.models.opportunity_status import OpportunityStatus
from app.package_integrity import calculate_content_hash


def can_execute(package: ApplicationPackage) -> bool:
    """
    Return True only when the application package has
    valid human approval for its exact current content.

    This function performs no external action.
    """

    if package.status != OpportunityStatus.APPROVED:
        return False

    if not package.human_approval_required:
        return False

    if not package.approved_by_human:
        return False

    if not package.content_hash:
        return False

    if not package.approved_content_hash:
        return False

    current_hash = calculate_content_hash(package)

    if current_hash != package.content_hash:
        return False

    if current_hash != package.approved_content_hash:
        return False

    if not package.claims_safe:
        return False

    if not package.resume_ready:
        return False

    return True


def execution_block_reason(
    package: ApplicationPackage,
) -> str:
    """
    Explain why execution is blocked.
    """

    if package.status != OpportunityStatus.APPROVED:
        return (
            f"Package status is "
            f"{package.status.value}, not APPROVED."
        )

    if not package.human_approval_required:
        return (
            "Human approval requirement is disabled."
        )

    if not package.approved_by_human:
        return (
            "Package has not been approved by a human."
        )

    if not package.content_hash:
        return (
            "Package has no content hash."
        )

    if not package.approved_content_hash:
        return (
            "Package has no approved content hash."
        )

    current_hash = calculate_content_hash(package)

    if current_hash != package.content_hash:
        return (
            "Current package content does not match "
            "its stored content hash."
        )

    if current_hash != package.approved_content_hash:
        return (
            "Current package content does not match "
            "the content approved by the human reviewer."
        )

    if not package.claims_safe:
        return (
            "Package contains unsafe claims."
        )

    if not package.resume_ready:
        return (
            "Resume is not ready."
        )

    return "Execution is permitted."
