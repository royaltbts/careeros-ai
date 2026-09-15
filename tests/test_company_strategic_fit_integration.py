import json
from pathlib import Path
import unittest

from app.job_batch_scorer import (
    load_candidate,
    load_evidence,
    load_strategy,
    load_intelligence_files,
    load_company_intelligence,
    score_job,
)

from app.company_strategic_fit import (
    calculate_company_strategic_fit,
)

from app.models.company_intelligence import (
    CompanyFact,
    CompanyIntelligence,
)


class CompanyStrategicFitIntegrationTest(unittest.TestCase):


    def test_web_research_confidence_reflects_research_quality(self):
        strategy = load_strategy()

        intelligence = CompanyIntelligence(
            company="Example SaaS",
            likely_cs_priorities=[
                "Customer satisfaction",
            ],
            facts=[
                CompanyFact(
                    category="Industry",
                    fact="Software",
                    source="https://example.com/industry",
                    confidence="HIGH",
                ),
            ],
            research_status="WEB_RESEARCHED",
            human_review_required=True,
        )

        result = calculate_company_strategic_fit(
            intelligence,
            strategy,
        )

        self.assertEqual(
            result["research_status"],
            "WEB_RESEARCHED",
        )
        self.assertLess(
            result["research_confidence"],
            100.0,
        )
        self.assertGreater(
            result["research_confidence"],
            0.0,
        )



    def test_research_quality_dimensions_are_exposed(self):
        strategy = load_strategy()

        intelligence = CompanyIntelligence(
            company="Example SaaS",
            likely_cs_priorities=[
                "Customer satisfaction",
            ],
            facts=[
                CompanyFact(
                    category="Industry",
                    fact="Software",
                    source="https://example.com/industry",
                    confidence="HIGH",
                ),
                CompanyFact(
                    category="CS Priority",
                    fact="Retention",
                    source="https://example.com/customers",
                    confidence="MEDIUM",
                ),
            ],
            research_status="WEB_RESEARCHED",
            human_review_required=True,
        )

        result = calculate_company_strategic_fit(
            intelligence,
            strategy,
        )

        self.assertIn(
            "research_coverage",
            result,
        )
        self.assertIn(
            "research_evidence_confidence",
            result,
        )
        self.assertIn(
            "research_quality",
            result,
        )

        self.assertGreaterEqual(
            result["research_coverage"],
            0.0,
        )
        self.assertLessEqual(
            result["research_coverage"],
            100.0,
        )

        self.assertGreaterEqual(
            result["research_evidence_confidence"],
            0.0,
        )
        self.assertLessEqual(
            result["research_evidence_confidence"],
            100.0,
        )

        self.assertGreaterEqual(
            result["research_quality"],
            0.0,
        )
        self.assertLessEqual(
            result["research_quality"],
            100.0,
        )

    def test_company_strategic_fit_integration(self):
        candidate = load_candidate()
        evidence = load_evidence()
        strategy = load_strategy()
        intelligence_jobs = load_intelligence_files()

        assert intelligence_jobs, "No Job Intelligence records found"

        intelligence = intelligence_jobs[0]

        company_intelligence = load_company_intelligence(
            intelligence.job_id
        )

        assert company_intelligence.company == intelligence.company
        assert company_intelligence.research_status == "ROLE_DERIVED"

        result = score_job(
            intelligence,
            candidate,
            evidence,
            strategy,
        )

        assert "company_strategic_fit" in result
        assert result["company_strategic_fit"] is not None

        strategic_fit = result["company_strategic_fit"]

        assert "strategic_alignment" in strategic_fit
        assert "research_confidence" in strategic_fit
        assert "decision_ready_fit" in strategic_fit
        assert "human_review_required" in strategic_fit
        assert strategic_fit["human_review_required"] is True

        ranking_file = Path(
            "data/jobs/ranked_opportunities.json"
        )

        assert ranking_file.exists(), "Ranking file does not exist"

        data = json.loads(
            ranking_file.read_text(encoding="utf-8")
        )

        assert data["opportunities"], "No opportunities persisted"

        persisted = next(
            item
            for item in data["opportunities"]
            if item["job_id"] == intelligence.job_id
        )

        assert "company_strategic_fit" in persisted
        assert persisted["company_strategic_fit"] is not None
