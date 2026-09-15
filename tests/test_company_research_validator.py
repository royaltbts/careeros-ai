import unittest

from app.company_research import CompanyResearchResult
from app.company_research_validator import validate_research
from app.models.company_intelligence import CompanyFact


class CompanyResearchValidatorTest(unittest.TestCase):

    def test_valid_research_passes(self):
        research = CompanyResearchResult(
            company="Example SaaS",
            facts=[
                CompanyFact(
                    category="Industry",
                    fact="Software",
                    source="https://example.com/company",
                    confidence="HIGH",
                ),
                CompanyFact(
                    category="CS Priority",
                    fact="Customer retention",
                    source="https://example.com/customers",
                    confidence="MEDIUM",
                ),
            ],
            research_status="WEB_RESEARCHED",
        )

        is_valid, errors = validate_research(
            research
        )

        self.assertTrue(is_valid)
        self.assertEqual(errors, [])

    def test_web_researched_without_facts_is_blocked(self):
        research = CompanyResearchResult(
            company="Example SaaS",
            facts=[],
            research_status="WEB_RESEARCHED",
        )

        is_valid, errors = validate_research(
            research
        )

        self.assertFalse(is_valid)
        self.assertTrue(
            any(
                "requires at least one fact" in error
                for error in errors
            )
        )

    def test_missing_source_is_blocked(self):
        research = CompanyResearchResult(
            company="Example SaaS",
            facts=[
                CompanyFact(
                    category="Industry",
                    fact="Software",
                    source="",
                    confidence="HIGH",
                ),
            ],
            research_status="WEB_RESEARCHED",
        )

        is_valid, errors = validate_research(
            research
        )

        self.assertFalse(is_valid)
        self.assertTrue(
            any(
                "source is missing" in error
                for error in errors
            )
        )

    def test_invalid_confidence_is_blocked(self):
        research = CompanyResearchResult(
            company="Example SaaS",
            facts=[
                CompanyFact(
                    category="Industry",
                    fact="Software",
                    source="https://example.com/company",
                    confidence="CERTAIN",
                ),
            ],
            research_status="WEB_RESEARCHED",
        )

        is_valid, errors = validate_research(
            research
        )

        self.assertFalse(is_valid)
        self.assertTrue(
            any(
                "invalid confidence" in error
                for error in errors
            )
        )

    def test_invalid_source_url_is_blocked(self):
        research = CompanyResearchResult(
            company="Example SaaS",
            facts=[
                CompanyFact(
                    category="Industry",
                    fact="Software",
                    source="not-a-url",
                    confidence="HIGH",
                ),
            ],
            research_status="WEB_RESEARCHED",
        )

        is_valid, errors = validate_research(
            research
        )

        self.assertFalse(is_valid)
        self.assertTrue(
            any(
                "valid HTTP/HTTPS URL" in error
                for error in errors
            )
        )

    def test_missing_fact_is_blocked(self):
        research = CompanyResearchResult(
            company="Example SaaS",
            facts=[
                CompanyFact(
                    category="Industry",
                    fact="",
                    source="https://example.com/company",
                    confidence="HIGH",
                ),
            ],
            research_status="WEB_RESEARCHED",
        )

        is_valid, errors = validate_research(
            research
        )

        self.assertFalse(is_valid)
        self.assertTrue(
            any(
                "fact text is missing" in error
                for error in errors
            )
        )

    def test_missing_category_is_blocked(self):
        research = CompanyResearchResult(
            company="Example SaaS",
            facts=[
                CompanyFact(
                    category="",
                    fact="Software",
                    source="https://example.com/company",
                    confidence="HIGH",
                ),
            ],
            research_status="WEB_RESEARCHED",
        )

        is_valid, errors = validate_research(
            research
        )

        self.assertFalse(is_valid)
        self.assertTrue(
            any(
                "category is missing" in error
                for error in errors
            )
        )


if __name__ == "__main__":
    unittest.main()
