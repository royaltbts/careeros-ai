import unittest

from app.application_effort import build_application_effort
from app.application_effort_store import (
    load_application_effort,
    save_application_effort,
)
from app.models.opportunity_decision import OpportunityDecision


class ApplicationEffortStoreTest(unittest.TestCase):

    def test_save_and_reload_application_effort(self):

        decision = OpportunityDecision(
            job_id="TEST-EFFORT-001",
            company="Test Company",
            title="Customer Success Manager",
            opportunity_score=95,
            priority="HIGH",
            recommendation="APPLY",
            human_review_required=True,
        )

        effort = build_application_effort(
            decision
        )

        path = save_application_effort(
            effort
        )

        self.assertTrue(
            path.exists()
        )

        loaded = load_application_effort(
            "TEST-EFFORT-001"
        )

        self.assertEqual(
            loaded.job_id,
            effort.job_id,
        )

        self.assertEqual(
            loaded.effort_level,
            "FULL",
        )

        self.assertEqual(
            loaded.recommendation,
            "APPLY",
        )


if __name__ == "__main__":
    unittest.main()
