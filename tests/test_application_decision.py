import unittest

from app.application_strategy import determine_application_decision


class ApplicationDecisionTest(unittest.TestCase):

    def test_high_priority_no_critical_gaps_returns_yes(self):
        opportunity = {
            "priority": "HIGH",
            "critical_gaps": [],
        }

        result = determine_application_decision(
            opportunity,
            {
                "human_review_required": True,
            },
        )

        self.assertEqual(result, "YES")

    def test_medium_priority_no_critical_gaps_returns_review(self):
        opportunity = {
            "priority": "MEDIUM",
            "critical_gaps": [],
        }

        result = determine_application_decision(
            opportunity,
            {},
        )

        self.assertEqual(result, "REVIEW")

    def test_low_priority_no_critical_gaps_returns_review(self):
        opportunity = {
            "priority": "LOW",
            "critical_gaps": [],
        }

        result = determine_application_decision(
            opportunity,
            {},
        )

        self.assertEqual(result, "REVIEW")

    def test_critical_gap_returns_conditional(self):
        opportunity = {
            "priority": "HIGH",
            "critical_gaps": ["Missing required capability"],
        }

        result = determine_application_decision(
            opportunity,
            {},
        )

        self.assertEqual(result, "CONDITIONAL")

    def test_company_review_does_not_override_high_priority(self):
        opportunity = {
            "priority": "HIGH",
            "critical_gaps": [],
        }

        result = determine_application_decision(
            opportunity,
            {
                "human_review_required": True,
            },
        )

        self.assertEqual(result, "YES")


if __name__ == "__main__":
    unittest.main()
