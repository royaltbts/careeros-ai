import unittest

from app.application_effort import (
    determine_effort_level,
    build_application_effort,
)
from app.models.opportunity_decision import OpportunityDecision


class ApplicationEffortTest(unittest.TestCase):

    def test_skip_requires_no_effort(self):
        level, _, actions = determine_effort_level(
            "SKIP",
            20,
        )

        self.assertEqual(level, "NONE")
        self.assertEqual(actions, [])

    def test_conditional_requires_limited_effort(self):
        level, _, actions = determine_effort_level(
            "CONDITIONAL",
            80,
        )

        self.assertEqual(level, "LIMITED")
        self.assertTrue(actions)

    def test_review_requires_targeted_effort(self):
        level, _, actions = determine_effort_level(
            "REVIEW",
            70,
        )

        self.assertEqual(level, "TARGETED")
        self.assertTrue(actions)

    def test_high_score_apply_requires_full_effort(self):
        level, _, actions = determine_effort_level(
            "APPLY",
            95,
        )

        self.assertEqual(level, "FULL")
        self.assertIn("Tailor resume", actions)

    def test_lower_apply_score_requires_targeted_effort(self):
        level, _, actions = determine_effort_level(
            "APPLY",
            81,
        )

        self.assertEqual(level, "TARGETED")
        self.assertIn("Tailor resume", actions)

    def test_effort_model_preserves_decision(self):
        decision = OpportunityDecision(
            job_id="TEST-001",
            company="Test Company",
            title="Customer Success Manager",
            opportunity_score=95,
            priority="HIGH",
            recommendation="APPLY",
            human_review_required=True,
        )

        effort = build_application_effort(decision)

        self.assertEqual(effort.recommendation, "APPLY")
        self.assertEqual(effort.effort_level, "FULL")
        self.assertEqual(effort.job_id, "TEST-001")


if __name__ == "__main__":
    unittest.main()


def test_apply_score_at_full_effort_threshold_is_full():
    level, _, actions = determine_effort_level(
        "APPLY",
        90,
    )

    assert level == "FULL"
    assert "Tailor resume" in actions
