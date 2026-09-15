import unittest

from app.company_research import CompanyResearchResult
from app.company_research_quality import (
    calculate_research_quality,
)
from app.models.company_intelligence import CompanyFact


class CompanyResearchQualityTest(unittest.TestCase):

    def test_complete_research_scores_high(self):
        research = CompanyResearchResult(
            company="Example SaaS",
            facts=[
                CompanyFact(
                    category="Industry",
                    fact="Software",
                    source="https://example.com/industry",
                    confidence="HIGH",
                ),
                CompanyFact(
                    category="Product",
                    fact="Customer success platform",
                    source="https://example.com/product",
                    confidence="HIGH",
                ),
                CompanyFact(
                    category="Customer Segments",
                    fact="Mid-market SaaS companies",
                    source="https://example.com/customers",
                    confidence="HIGH",
                ),
                CompanyFact(
                    category="Business Model",
                    fact="B2B subscription",
                    source="https://example.com/model",
                    confidence="HIGH",
                ),
                CompanyFact(
                    category="Company Stage",
                    fact="Growth stage",
                    source="https://example.com/about",
                    confidence="MEDIUM",
                ),
                CompanyFact(
                    category="Customer Success Model",
                    fact="High-touch customer success",
                    source="https://example.com/customers",
                    confidence="HIGH",
                ),
                CompanyFact(
                    category="CS Priority",
                    fact="Retention",
                    source="https://example.com/customers",
                    confidence="HIGH",
                ),
                CompanyFact(
                    category="Risk",
                    fact="Competitive market",
                    source="https://example.com/risk",
                    confidence="MEDIUM",
                ),
            ],
            research_status="WEB_RESEARCHED",
        )

        result = calculate_research_quality(
            research
        )

        self.assertGreaterEqual(
            result["score"],
            90,
        )
        self.assertEqual(
            result["coverage"],
            100.0,
        )

    def test_partial_research_scores_lower(self):
        research = CompanyResearchResult(
            company="Example SaaS",
            facts=[
                CompanyFact(
                    category="Industry",
                    fact="Software",
                    source="https://example.com/industry",
                    confidence="HIGH",
                ),
                CompanyFact(
                    category="Product",
                    fact="Customer success platform",
                    source="https://example.com/product",
                    confidence="HIGH",
                ),
                CompanyFact(
                    category="CS Priority",
                    fact="Retention",
                    source="https://example.com/customers",
                    confidence="HIGH",
                ),
            ],
            research_status="WEB_RESEARCHED",
        )

        result = calculate_research_quality(
            research
        )

        self.assertLess(
            result["score"],
            90,
        )
        self.assertGreater(
            result["score"],
            0,
        )
        self.assertLess(
            result["coverage"],
            100.0,
        )

    def test_confidence_affects_quality(self):
        high = CompanyResearchResult(
            company="Example SaaS",
            facts=[
                CompanyFact(
                    category="Industry",
                    fact="Software",
                    source="https://example.com",
                    confidence="HIGH",
                ),
            ],
            research_status="WEB_RESEARCHED",
        )

        low = CompanyResearchResult(
            company="Example SaaS",
            facts=[
                CompanyFact(
                    category="Industry",
                    fact="Software",
                    source="https://example.com",
                    confidence="LOW",
                ),
            ],
            research_status="WEB_RESEARCHED",
        )

        high_result = calculate_research_quality(high)
        low_result = calculate_research_quality(low)

        self.assertGreater(
            high_result["score"],
            low_result["score"],
        )

    def test_non_web_research_is_not_treated_as_full_research(self):
        research = CompanyResearchResult(
            company="Example SaaS",
            facts=[
                CompanyFact(
                    category="Industry",
                    fact="Software",
                    source="https://example.com",
                    confidence="HIGH",
                ),
            ],
            research_status="ROLE_DERIVED",
        )

        result = calculate_research_quality(
            research
        )

        self.assertEqual(
            result["status"],
            "ROLE_DERIVED",
        )
        self.assertLess(
            result["score"],
            100,
        )


if __name__ == "__main__":
    unittest.main()
