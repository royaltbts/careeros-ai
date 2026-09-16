import unittest

from app.job_location import evaluate_location
from app.models.career_strategy import CareerStrategy


def strategy():
    return CareerStrategy(
        primary_direction="Customer Success",
        target_roles=["Customer Success Manager"],
        preferred_seniority=["Manager"],
        geography="Any",
        priority_capabilities=["Customer Success"],
        avoid_roles=[],
        strategy_notes=[],
    )


class TestJobLocation(unittest.TestCase):

    def test_local_hyderabad_hybrid_is_eligible(self):
        result = evaluate_location(
            "Hyderabad, India",
            "hybrid",
            strategy(),
        )

        self.assertTrue(result.eligible)
        self.assertEqual(result.confidence, 1.0)
        self.assertFalse(result.verification_required)

    def test_outside_india_on_site_is_not_eligible(self):
        result = evaluate_location(
            "London, UK",
            "on-site",
            strategy(),
        )

        self.assertFalse(result.eligible)
        self.assertEqual(result.confidence, 1.0)
        self.assertFalse(result.verification_required)

    def test_outside_india_remote_is_eligible(self):
        result = evaluate_location(
            "London, UK",
            "remote",
            strategy(),
        )

        self.assertTrue(result.eligible)
        self.assertEqual(result.confidence, 1.0)
        self.assertFalse(result.verification_required)

    def test_missing_work_mode_requires_verification(self):
        result = evaluate_location(
            "London, UK",
            None,
            strategy(),
        )

        self.assertTrue(result.eligible)
        self.assertEqual(result.confidence, 0.5)
        self.assertTrue(result.verification_required)


if __name__ == "__main__":
    unittest.main()
