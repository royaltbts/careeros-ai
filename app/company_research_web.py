from agents import Agent, Runner, WebSearchTool

from app.company_research import CompanyResearchResult
from app.models.company_intelligence import CompanyFact
from app.company_research_source import CompanyResearchSource


class OpenAIWebCompanyResearchSource(CompanyResearchSource):
    """
    Company research source backed by OpenAI WebSearchTool.

    This adapter retrieves source-backed company facts.
    It does not approve, tailor, apply, or contact anyone.
    """

    def __init__(
        self,
        search_context_size: str = "medium",
    ):
        self.search_tool = WebSearchTool(
            search_context_size=search_context_size,
        )

    def research(
        self,
        company: str,
    ) -> CompanyResearchResult:

        agent = Agent(
            name="Company Research Agent",
            instructions=(
                "Research the specified company using web search. "
                "Return only source-backed facts. "
                "Do not invent or infer unsupported facts. "
                "Each fact must include a category, factual statement, "
                "source URL, and confidence level of HIGH, MEDIUM, or LOW. "
                "Focus on industry, product/service, customer segments, "
                "business model, company stage, customer success model, "
                "customer success priorities, and relevant risks. "
                "Every factual claim must have a source."
            ),
            tools=[self.search_tool],
            output_type=CompanyResearchResult,
        )

        result = Runner.run_sync(
            agent,
            (
                f"Research the company: {company}. "
                "Produce source-backed company intelligence."
            ),
        )

        return result.final_output_as(CompanyResearchResult, raise_if_incorrect_type=True)
