import unittest

from app.models.candidate_finding import CandidateFinding
from app.risk_agent import build_risk_finding
from app.supervisor_case import build_supervisor_case


class CandidateRiskHandoffTest(unittest.TestCase):

    def candidate_finding(self):
        return CandidateFinding(
            strengths=[
                "Customer communication",
                "Customer satisfaction",
                "Process improvement",
            ],
            transferable_experience=[
                "Operations leadership transferable to Customer Success."
            ],
            verified_evidence_refs=[
                "EV001",
                "EV003",
                "EV004",
            ],
            explicit_gaps=[
                "Formal SaaS experience",
                "CRM expertise",
                "Enterprise account ownership",
            ],
            forbidden_assumptions=[
                "SaaS experience",
                "CRM expertise",
                "Enterprise account ownership",
            ],
            recommendation="APPLY",
            confidence=0.90,
        )

    def opportunity(self):
        return {
            "job_id": "TEST-HANDOFF-001",
            "company": "Example SaaS",
            "title": "Customer Success Manager",
            "fit_score": 100.0,
            "opportunity_score": 100.0,
            "priority": "HIGH",
            "critical_gaps": [],
            "core_gaps": [],
            "requirement_analysis": [],
            "company_strategic_fit": {
                "strategic_alignment": 100.0,
                "research_quality": 100.0,
            },
        }

    def decision(self):
        return {
            "job_id": "TEST-HANDOFF-001",
            "company": "Example SaaS",
            "title": "Customer Success Manager",
            "recommendation": "APPLY",
            "opportunity_score": 100.0,
            "priority": "HIGH",
            "critical_gaps": [],
            "transferable_opportunities": [],
        }

    def test_candidate_finding_reaches_risk_agent(self):
        candidate = self.candidate_finding()

        risk = build_risk_finding(
            self.opportunity(),
            self.decision(),
            candidate_finding=candidate,
        )

        self.assertEqual(
            risk.agent,
            "Risk Agent",
        )

        self.assertEqual(
            risk.recommendation,
            "APPLY",
        )

        self.assertEqual(
            risk.evidence_refs,
            [
                "EV001",
                "EV003",
                "EV004",
            ],
        )

    def test_risk_agent_classifies_transition_gaps_as_non_blocking(self):
        risk = build_risk_finding(
            self.opportunity(),
            self.decision(),
            candidate_finding=self.candidate_finding(),
        )

        self.assertEqual(
            risk.recommendation,
            "APPLY",
        )

        self.assertEqual(
            risk.confidence,
            0.85,
        )

        self.assertIn(
            "Non-blocking transition risk",
            risk.finding,
        )

        self.assertIn(
            "Formal SaaS experience",
            risk.finding,
        )

        self.assertIn(
            "CRM expertise",
            risk.finding,
        )

        self.assertIn(
            "Enterprise account ownership",
            risk.finding,
        )

    def test_supervisor_case_preserves_candidate_risk_handoff(self):
        case = build_supervisor_case(
            self.opportunity(),
            self.decision(),
            candidate_finding=self.candidate_finding(),
        )

        risk = next(
            finding
            for finding in case.findings
            if finding.agent == "Risk Agent"
        )

        self.assertEqual(
            risk.recommendation,
            "APPLY",
        )

        self.assertEqual(
            risk.evidence_refs,
            [
                "EV001",
                "EV003",
                "EV004",
            ],
        )


if __name__ == "__main__":
    unittest.main()
