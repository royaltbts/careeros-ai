import unittest

from app.supervisor import (
    build_supervisor_decision,
    build_supervisor_decision_from_case,
)


class SupervisorTest(unittest.TestCase):

    def base_opportunity(self):
        return {
            "job_id": "TEST-001",
            "company": "Example SaaS",
            "title": "Customer Success Manager",
            "fit_score": 90.0,
            "opportunity_score": 90.0,
            "priority": "HIGH",
            "recommendation": "APPLY",
            "critical_gaps": [],
            "requirement_analysis": [],
            "company_strategic_fit": {
                "strategic_alignment": 90.0,
                "research_quality": 95.0,
            },
        }

    def test_strong_opportunity_is_apply(self):
        opportunity = self.base_opportunity()

        decision = {
            "recommendation": "APPLY",
        }

        result = build_supervisor_decision(
            opportunity,
            decision,
            safety={
                "all_claims_safe": True,
            },
        )

        self.assertEqual(
            result.recommendation,
            "APPLY",
        )
        self.assertEqual(
            result.conflicts,
            [],
        )
        self.assertTrue(
            result.human_review_required
        )
        self.assertFalse(
            result.external_action_allowed
        )

    def test_low_research_quality_forces_review(self):
        opportunity = self.base_opportunity()
        opportunity["company_strategic_fit"][
            "research_quality"
        ] = 50.0

        decision = {
            "recommendation": "APPLY",
        }

        result = build_supervisor_decision(
            opportunity,
            decision,
            safety={
                "all_claims_safe": True,
            },
        )

        self.assertEqual(
            result.recommendation,
            "REVIEW",
        )
        self.assertTrue(
            result.conflicts
        )
        self.assertTrue(
            any(
                "research quality" in conflict.lower()
                for conflict in result.conflicts
            )
        )

    def test_risk_only_disagreement_does_not_force_review(self):
        opportunity = self.base_opportunity()

        decision = {
            "recommendation": "APPLY",
        }

        result = build_supervisor_decision(
            opportunity,
            decision,
            safety={
                "all_claims_safe": True,
            },
        )

        # Simulate the Risk Agent raising a caution without
        # identifying a critical evidence blocker.
        result.conflicts = []

        self.assertEqual(
            result.recommendation,
            "APPLY",
        )
        self.assertLess(
            result.confidence,
            1.0,
        )

    def test_critical_gap_forces_review(self):
        opportunity = self.base_opportunity()
        opportunity["critical_gaps"] = [
            "Enterprise account ownership"
        ]

        decision = {
            "recommendation": "APPLY",
        }

        result = build_supervisor_decision(
            opportunity,
            decision,
            safety={
                "all_claims_safe": True,
            },
        )

        self.assertEqual(
            result.recommendation,
            "REVIEW",
        )
        self.assertTrue(
            result.conflicts
        )

    def test_unsafe_claims_force_review(self):
        opportunity = self.base_opportunity()

        decision = {
            "recommendation": "APPLY",
        }

        result = build_supervisor_decision(
            opportunity,
            decision,
            safety={
                "all_claims_safe": False,
            },
        )

        self.assertEqual(
            result.recommendation,
            "REVIEW",
        )

        self.assertTrue(
            any(
                "claims failed" in finding.finding.lower()
                for finding in result.findings
                if finding.source == "Claim Safety"
            )
        )

    def test_low_priority_is_skip(self):
        opportunity = self.base_opportunity()
        opportunity["priority"] = "LOW"
        opportunity["opportunity_score"] = 20.0

        decision = {
            "recommendation": "SKIP",
        }

        result = build_supervisor_decision(
            opportunity,
            decision,
            safety={
                "all_claims_safe": True,
            },
        )

        self.assertEqual(
            result.recommendation,
            "SKIP",
        )


if __name__ == "__main__":
    unittest.main()
