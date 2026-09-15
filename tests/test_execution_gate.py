import unittest

from app.careeros import load_existing_application_package
from app.execution_gate import can_execute, execution_block_reason
from app.models.opportunity_status import OpportunityStatus


class ExecutionGateTest(unittest.TestCase):

    def test_unapproved_application_is_blocked(self):
        package = load_existing_application_package("JOB-001")

        self.assertIsNotNone(package)
        self.assertFalse(package.approved_by_human)
        self.assertEqual(
            package.status,
            OpportunityStatus.PENDING_APPROVAL,
        )

        self.assertFalse(can_execute(package))

        self.assertIn(
            "not APPROVED",
            execution_block_reason(package),
        )


if __name__ == "__main__":
    unittest.main()
