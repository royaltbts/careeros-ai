from abc import ABC, abstractmethod

from app.company_research import CompanyResearchResult


class CompanyResearchSource(ABC):
    """
    Contract for any external company-research provider.

    The source layer retrieves facts.
    It does not decide whether those facts are safe
    for use in an application.
    """

    @abstractmethod
    def research(
        self,
        company: str,
    ) -> CompanyResearchResult:
        """
        Research a company and return source-backed facts.
        """
        raise NotImplementedError
