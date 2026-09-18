import json
import unittest

from app.evidence_matcher import match_requirement
from app.models.evidence import EvidenceItem


class EvidenceMatchingTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(
            "data/evidence/evidence.json",
            encoding="utf-8",
        ) as file:
            cls.evidence = [
                EvidenceItem.model_validate(item)
                for item in json.load(file)
            ]

    def test_business_review_is_direct(self):
        matches = match_requirement(
            "Lead customer business reviews",
            self.evidence,
        )

        ev001 = next(
            match
            for match in matches
            if match.evidence_id == "EV001"
        )

        self.assertEqual(
            ev001.match_type,
            "DIRECT",
        )

    def test_continuous_improvement_is_direct(self):
        matches = match_requirement(
            "Drive continuous improvement",
            self.evidence,
        )

        ev004 = next(
            match
            for match in matches
            if match.evidence_id == "EV004"
        )

        self.assertEqual(
            ev004.match_type,
            "DIRECT",
        )

    def test_customer_experience_metrics_are_direct(self):
        matches = match_requirement(
            "Work with customer experience metrics",
            self.evidence,
        )

        ev003 = next(
            match
            for match in matches
            if match.evidence_id == "EV003"
        )

        self.assertEqual(
            ev003.match_type,
            "DIRECT",
        )

    def test_enterprise_account_ownership_is_not_proven(self):
        matches = match_requirement(
            "Manage enterprise SaaS accounts for 5+ years",
            self.evidence,
        )

        self.assertEqual(
            matches,
            [],
        )

    def test_customer_health_is_transferable(self):
        matches = match_requirement(
            "Customer health",
            self.evidence,
        )

        ev003 = next(
            match
            for match in matches
            if match.evidence_id == "EV003"
        )

        self.assertEqual(
            ev003.match_type,
            "TRANSFERABLE",
        )

    def test_strategic_csm_has_direct_and_transferable_evidence(self):
        from app.application_strategy import build_strategy

        opportunity = {
            "job_id": "JOB-002",
            "company": "Example Company",
            "title": "Strategic Customer Success Manager",
            "priority": "HIGH",
            "fit_score": 90.0,
            "opportunity_score": 90.0,
            "critical_gaps": [],
            "core_gaps": [],
        }

        strategy = build_strategy(
            opportunity,
            self.evidence,
        )

        self.assertIn(
            "CUSTOMER_COMMUNICATION",
            strategy.evidence_strengths,
        )
        self.assertIn(
            "CUSTOMER_SATISFACTION",
            strategy.transferable_capabilities,
        )

    def test_technical_csm_requirements_remain_missing(self):
        from app.profile_tailor import build_profile_tailor

        result, evidence_map = build_profile_tailor(
            "JOB-003"
        )

        expected = {
            "Advanced SQL",
            "Snowflake",
            "Power BI development",
            "Technical integrations",
            "SaaS experience",
            "CRM experience",
        }

        self.assertEqual(
            set(result.missing_requirements),
            expected,
        )

        for mapping in evidence_map:
            self.assertEqual(
                mapping.match_type,
                "MISSING",
            )
            self.assertEqual(
                mapping.evidence_ids,
                [],
            )
            self.assertFalse(
                mapping.allowed,
            )
            self.assertTrue(
                mapping.human_review_required,
            )


if __name__ == "__main__":
    unittest.main()
