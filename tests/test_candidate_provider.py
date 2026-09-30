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


    def test_llm_output_must_be_validated_against_verified_evidence(self):
        result = build_candidate_finding_with_provider(
            self.candidate(),
            self.evidence(),
            provider="mock",
        )

        verified_ids = {
            item.id
            for item in self.evidence()
            if item.status == "VERIFIED"
        }

        self.assertTrue(
            set(result.verified_evidence_refs).issubset(
                verified_ids
            )
        )


    def test_candidate_finding_validator_rejects_unverified_evidence(self):
        from app.candidate_finding_validator import validate_candidate_finding
        from app.models.candidate_finding import CandidateFinding

        finding = CandidateFinding(
            verified_evidence_refs=["EV001", "FAKE001"]
        )

        with self.assertRaises(ValueError):
            validate_candidate_finding(
                finding,
                self.evidence(),
            )


    def test_openai_provider_rejects_unverified_llm_evidence(self):
        from unittest.mock import patch
        from app.models.candidate_finding import CandidateFinding

        fake_finding = CandidateFinding(
            verified_evidence_refs=["EV001", "FAKE001"]
        )

        with patch(
            "app.candidate_provider.Runner.run_sync"
        ) as mock_run:
            mock_run.return_value.final_output = fake_finding

            with self.assertRaises(ValueError):
                build_candidate_finding_with_provider(
                    self.candidate(),
                    self.evidence(),
                    provider="openai",
                )



if __name__ == "__main__":
    unittest.main()
