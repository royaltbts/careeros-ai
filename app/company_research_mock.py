from app.company_research import CompanyResearchResult
from app.company_research_source import CompanyResearchSource
from app.models.company_intelligence import CompanyFact


class MockCompanyResearchSource(CompanyResearchSource):
    """
    Deterministic research source used for local testing.

    These are synthetic facts and must never be presented
    as real company research.
    """

    def research(
        self,
        company: str,
    ) -> CompanyResearchResult:

        fixtures = {
            "CustomerFirst SaaS": [
                CompanyFact(
                    category="Industry",
                    fact="Synthetic SaaS company serving business customers.",
                    source="MOCK_SOURCE",
                    confidence="LOW",
                ),
                CompanyFact(
                    category="Product",
                    fact="Synthetic customer-facing SaaS platform.",
                    source="MOCK_SOURCE",
                    confidence="LOW",
                ),
                CompanyFact(
                    category="CS Priority",
                    fact="Customer retention",
                    source="MOCK_SOURCE",
                    confidence="LOW",
                ),
                CompanyFact(
                    category="CS Priority",
                    fact="Customer adoption",
                    source="MOCK_SOURCE",
                    confidence="LOW",
                ),
                CompanyFact(
                    category="CS Priority",
                    fact="Customer experience",
                    source="MOCK_SOURCE",
                    confidence="LOW",
                ),
            ],
            "EnterpriseCloud": [
                CompanyFact(
                    category="Industry",
                    fact="Synthetic enterprise cloud technology company.",
                    source="MOCK_SOURCE",
                    confidence="LOW",
                ),
                CompanyFact(
                    category="Product",
                    fact="Synthetic enterprise cloud platform.",
                    source="MOCK_SOURCE",
                    confidence="LOW",
                ),
                CompanyFact(
                    category="CS Priority",
                    fact="Strategic account engagement",
                    source="MOCK_SOURCE",
                    confidence="LOW",
                ),
                CompanyFact(
                    category="CS Priority",
                    fact="Customer adoption",
                    source="MOCK_SOURCE",
                    confidence="LOW",
                ),
                CompanyFact(
                    category="CS Priority",
                    fact="Customer retention",
                    source="MOCK_SOURCE",
                    confidence="LOW",
                ),
            ],
            "TechSupport Pro": [
                CompanyFact(
                    category="Industry",
                    fact="Synthetic technical support technology company.",
                    source="MOCK_SOURCE",
                    confidence="LOW",
                ),
                CompanyFact(
                    category="Product",
                    fact="Synthetic technical support platform.",
                    source="MOCK_SOURCE",
                    confidence="LOW",
                ),
                CompanyFact(
                    category="CS Priority",
                    fact="Technical integrations",
                    source="MOCK_SOURCE",
                    confidence="LOW",
                ),
                CompanyFact(
                    category="CS Priority",
                    fact="Troubleshooting",
                    source="MOCK_SOURCE",
                    confidence="LOW",
                ),
                CompanyFact(
                    category="CS Priority",
                    fact="Support reliability",
                    source="MOCK_SOURCE",
                    confidence="LOW",
                ),
            ],
        }

        facts = fixtures.get(
            company,
            [
                CompanyFact(
                    category="Industry",
                    fact=f"{company} operates in a synthetic test industry.",
                    source="MOCK_SOURCE",
                    confidence="LOW",
                ),
                CompanyFact(
                    category="Product",
                    fact=f"{company} provides a synthetic test product.",
                    source="MOCK_SOURCE",
                    confidence="LOW",
                ),
                CompanyFact(
                    category="CS Priority",
                    fact="Customer retention",
                    source="MOCK_SOURCE",
                    confidence="LOW",
                ),
            ],
        )

        return CompanyResearchResult(
            company=company,
            facts=facts,
            research_status="MOCK",
        )
