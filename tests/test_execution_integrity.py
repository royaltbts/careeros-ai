import copy
import unittest

from app.careeros import load_existing_application_package
from app.execution_gate import can_execute, execution_block_reason
from app.models.opportunity_status import OpportunityStatus
from app.package_integrity import calculate_content_hash


class ExecutionIntegrityTest(unittest.TestCase):

    def test_approved_unchanged_package_can_execute(self):
        package = load_existing_application_package("JOB-001")

        self.assertIsNotNone(package)

        package = copy.deepcopy(package)

        package.status = OpportunityStatus.APPROVED
        package.approved_by_human = True
        package.content_hash = calculate_content_hash(package)
        package.approved_content_hash = package.content_hash

        self.assertTrue(can_execute(package))

    def test_unsafe_claims_block_execution(self):
        package = load_existing_application_package("JOB-001")
        self.assertIsNotNone(package)
        package = copy.deepcopy(package)
        package.status = OpportunityStatus.APPROVED
        package.approved_by_human = True
        package.claims_safe = False
        package.content_hash = calculate_content_hash(package)
        package.approved_content_hash = package.content_hash

        self.assertFalse(can_execute(package))
        self.assertIn(
            "unsafe claims",
            execution_block_reason(package),
        )

    def test_unready_resume_blocks_execution(self):
        package = load_existing_application_package("JOB-001")
        self.assertIsNotNone(package)
        package = copy.deepcopy(package)
        package.status = OpportunityStatus.APPROVED
        package.approved_by_human = True
        package.resume_ready = False
        package.content_hash = calculate_content_hash(package)
        package.approved_content_hash = package.content_hash

        self.assertFalse(can_execute(package))
        self.assertIn(
            "Resume is not ready",
            execution_block_reason(package),
        )

    def test_changed_content_after_approval_is_blocked(self):
        package = load_existing_application_package("JOB-001")

        self.assertIsNotNone(package)

        package = copy.deepcopy(package)

        package.status = OpportunityStatus.APPROVED
        package.approved_by_human = True
        package.content_hash = calculate_content_hash(package)
        package.approved_content_hash = package.content_hash

        original_hash = package.approved_content_hash

        package.resume.summary = (
            package.resume.summary
            + " Unauthorized content change."
        )

        self.assertNotEqual(
            calculate_content_hash(package),
            original_hash,
        )

        self.assertFalse(can_execute(package))

        self.assertIn(
            "content hash",
            execution_block_reason(package),
        )


if __name__ == "__main__":
    unittest.main()
