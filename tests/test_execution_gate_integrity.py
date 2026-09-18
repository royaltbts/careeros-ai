import copy

from app.careeros import load_existing_application_package
from app.execution_gate import can_execute, execution_block_reason
from app.models.opportunity_status import OpportunityStatus
from app.package_integrity import calculate_content_hash


def approved_package():
    package = load_existing_application_package("JOB-001")
    assert package is not None
    package = copy.deepcopy(package)
    package.status = OpportunityStatus.APPROVED
    package.human_approval_required = True
    package.approved_by_human = True
    package.claims_safe = True
    package.resume_ready = True
    package.content_hash = calculate_content_hash(package)
    package.approved_content_hash = package.content_hash
    return package


def test_modified_approved_package_is_blocked():
    package = approved_package()

    package.claims_safe = False

    assert not can_execute(package)
    assert "stored content hash" in execution_block_reason(package)
