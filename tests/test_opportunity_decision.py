import unittest

from app.opportunity_decision import build_opportunity_decision


def make_opportunity(
    priority: str,
    critical_gaps=None,
    score: float = 80.0,
):
    return {
        "job_id": "TEST-001",
        "company": "Test Company",
        "title": "Customer Success Manager",
        "opportunity_score": score,
        "priority": priority,
        "fit_score": 80.0,
        "critical_gaps": critical_gaps or [],
        "core_gaps": [],
        "company_strategic_fit": None,
    }


class OpportunityDecisionTest(unittest.TestCase):

    def test_high_without_gaps_is_apply(self):
        decision = build_opportunity_decision(
            make_opportunity("HIGH")
        )
        self.assertEqual(
            decision.recommendation,
            "APPLY",
        )

    def test_high_with_critical_gap_is_conditional(self):
        decision = build_opportunity_decision(
            make_opportunity(
                "HIGH",
                ["Enterprise account ownership"],
            )
        )
        self.assertEqual(
            decision.recommendation,
            "CONDITIONAL",
        )

    def test_medium_without_gaps_is_review(self):
        decision = build_opportunity_decision(
            make_opportunity("MEDIUM")
        )
        self.assertEqual(
            decision.recommendation,
            "REVIEW",
        )

    def test_medium_with_critical_gap_is_conditional(self):
        decision = build_opportunity_decision(
            make_opportunity(
                "MEDIUM",
                ["Advanced SQL"],
            )
        )
        self.assertEqual(
            decision.recommendation,
            "CONDITIONAL",
        )

    def test_low_without_gaps_is_skip(self):
        decision = build_opportunity_decision(
            make_opportunity(
                "LOW",
                score=30.0,
            )
        )
        self.assertEqual(
            decision.recommendation,
            "SKIP",
        )

    def test_low_with_critical_gaps_is_still_skip(self):
        decision = build_opportunity_decision(
            make_opportunity(
                "LOW",
                ["Advanced SQL", "Snowflake"],
                score=0.0,
            )
        )
        self.assertEqual(
            decision.recommendation,
            "SKIP",
        )

    def test_human_review_is_always_required(self):
        for priority in [
            "HIGH",
            "MEDIUM",
            "LOW",
        ]:
            decision = build_opportunity_decision(
                make_opportunity(priority)
            )
            self.assertTrue(
                decision.human_review_required
            )


if __name__ == "__main__":
    unittest.main()


def test_high_priority_with_limited_research_requires_review():
    opportunity = {
        "job_id": "JOB-RESEARCH-001",
        "company": "ResearchLimitedCo",
        "title": "Customer Success Manager",
        "opportunity_score": 90,
        "priority": "HIGH",
        "fit_score": 90,
        "critical_gaps": [],
        "core_gaps": [],
        "company_strategic_fit": {
            "strategic_alignment": 100,
            "research_confidence": 0,
            "decision_ready_fit": 0,
        },
    }

    decision = build_opportunity_decision(opportunity)

    assert decision.recommendation == "APPLY"
    assert any(
        "Company research confidence is limited" in reason
        for reason in decision.decision_reasons
    )


def test_high_priority_with_strong_research_can_apply():
    opportunity = {
        "job_id": "JOB-RESEARCH-002",
        "company": "WellResearchedCo",
        "title": "Customer Success Manager",
        "opportunity_score": 90,
        "priority": "HIGH",
        "fit_score": 90,
        "critical_gaps": [],
        "core_gaps": [],
        "company_strategic_fit": {
            "strategic_alignment": 100,
            "research_confidence": 100,
            "decision_ready_fit": 100,
        },
    }

    decision = build_opportunity_decision(opportunity)

    assert decision.recommendation == "APPLY"


def test_critical_gap_overrides_research_confidence():
    opportunity = {
        "job_id": "JOB-RESEARCH-003",
        "company": "GapCo",
        "title": "Customer Success Manager",
        "opportunity_score": 90,
        "priority": "HIGH",
        "fit_score": 90,
        "critical_gaps": ["Advanced SQL"],
        "core_gaps": [],
        "company_strategic_fit": {
            "strategic_alignment": 100,
            "research_confidence": 100,
            "decision_ready_fit": 100,
        },
    }

    decision = build_opportunity_decision(opportunity)

    assert decision.recommendation == "CONDITIONAL"


def test_core_gaps_are_exposed_as_transferable_opportunities():
    opportunity = {
        "job_id": "JOB-CORE-001",
        "company": "CoreGapCo",
        "title": "Customer Success Manager",
        "opportunity_score": 70,
        "priority": "MEDIUM",
        "fit_score": 70,
        "critical_gaps": [],
        "core_gaps": ["SaaS experience", "CRM experience"],
        "company_strategic_fit": None,
    }

    decision = build_opportunity_decision(opportunity)

    assert decision.recommendation == "REVIEW"
    assert decision.transferable_opportunities == [
        "SaaS experience",
        "CRM experience",
    ]
    assert any(
        "2 core capability gap(s)" in reason
        for reason in decision.decision_reasons
    )
