import unittest

from app.models.opportunity_decision_audit import (
    OpportunityDecisionAudit,
)


class OpportunityDecisionAuditTest(unittest.TestCase):

    def test_valid_audit_record(self):

        audit = OpportunityDecisionAudit(
            job_id="JOB-001",
            company="CustomerFirst SaaS",
            title="Customer Success Manager",
            opportunity_score=100.0,
            priority="HIGH",
            recommendation="APPLY",
            decision_reasons=[
                "No critical evidence gaps",
            ],
            strengths=[
                "Strong candidate fit",
            ],
        )

        self.assertEqual(
            audit.job_id,
            "JOB-001",
        )

        self.assertEqual(
            audit.recommendation,
            "APPLY",
        )

        self.assertEqual(
            audit.opportunity_score,
            100.0,
        )

        self.assertTrue(
            audit.human_review_required
        )

        self.assertIsNotNone(
            audit.recorded_at
        )


if __name__ == "__main__":
    unittest.main()
