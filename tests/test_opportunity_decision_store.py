import unittest

from app.opportunity_decision import (
    build_opportunity_decision,
)
from app.opportunity_decision_store import (
    load_opportunity_decision,
    save_opportunity_decision,
)


class OpportunityDecisionStoreTest(unittest.TestCase):

    def test_save_and_reload_decision(self):

        opportunity = {
            "job_id": "TEST-DECISION-001",
            "company": "Test Company",
            "title": "Customer Success Manager",
            "opportunity_score": 95,
            "priority": "HIGH",
            "fit_score": 95,
            "critical_gaps": [],
            "core_gaps": [],
            "company_strategic_fit": {
                "strategic_alignment": 100,
                "research_confidence": 100,
                "decision_ready_fit": 100,
            },
        }

        decision = build_opportunity_decision(
            opportunity
        )

        path = save_opportunity_decision(
            decision
        )

        self.assertTrue(path.exists())

        loaded = load_opportunity_decision(
            "TEST-DECISION-001"
        )

        self.assertEqual(
            loaded.job_id,
            decision.job_id,
        )

        self.assertEqual(
            loaded.recommendation,
            "APPLY",
        )

        self.assertEqual(
            loaded.opportunity_score,
            95,
        )

        self.assertTrue(
            loaded.human_review_required
        )


if __name__ == "__main__":
    unittest.main()
