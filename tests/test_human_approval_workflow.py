import unittest

from app.human_approval_workflow import approve_application
from app.models.human_approval import HumanApproval
from app.models.opportunity_status import OpportunityStatus


class HumanApprovalWorkflowTest(unittest.TestCase):

    def test_new_approval_is_not_human_approved(self):
        approval = HumanApproval(
            job_id="TEST-001",
            company="Test Company",
            title="Customer Success Manager",
            resume_ready=True,
            cover_letter_ready=True,
            outreach_ready=True,
            claims_safe=True,
        )

        self.assertFalse(approval.approved_by_human)
        self.assertEqual(approval.decision, "PENDING")

    def test_approval_requires_pending_status(self):
        approval = HumanApproval(
            job_id="TEST-001",
            company="Test Company",
            title="Customer Success Manager",
            resume_ready=True,
            cover_letter_ready=True,
            outreach_ready=True,
            claims_safe=True,
        )

        with self.assertRaises(ValueError):
            approve_application(
                approval,
                OpportunityStatus.ANALYZED,
            )

        self.assertFalse(approval.approved_by_human)
        self.assertEqual(approval.decision, "PENDING")


if __name__ == "__main__":
    unittest.main()
