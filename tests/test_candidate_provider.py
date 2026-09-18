import unittest

from app.candidate_provider import build_candidate_finding_with_provider
from app.pipeline import load_candidate_profile, load_evidence


class CandidateProviderTest(unittest.TestCase):

    def candidate(self):
        return load_candidate_profile(
            "data/candidate/profile.json"
        )

    def evidence(self):
        return load_evidence(
            "data/evidence/evidence.json"
        )

    def test_mock_provider_returns_deterministic_candidate_finding(self):
        result = build_candidate_finding_with_provider(
            self.candidate(),
            self.evidence(),
            provider="mock",
        )

        self.assertEqual(result.agent, "Candidate Profile Analyst")
        self.assertEqual(
            result.verified_evidence_refs,
            ["EV001", "EV002", "EV003", "EV004", "EV005", "EV006", "EV007", "EV008"],
        )
        self.assertIn(
            "People management transferable to Customer Success leadership.",
            result.transferable_experience,
        )
        self.assertIn(
            "Formal SaaS experience",
            result.explicit_gaps,
        )
        self.assertIn(
            "SaaS experience",
            result.forbidden_assumptions,
        )
        self.assertEqual(result.recommendation, "APPLY")
        self.assertEqual(result.confidence, 0.90)


if __name__ == "__main__":
    unittest.main()
