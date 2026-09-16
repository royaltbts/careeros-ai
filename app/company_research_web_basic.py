from datetime import datetime, timezone
import re
from html import unescape
from urllib.parse import urljoin

import requests

from app.company_research import CompanyResearchResult
from app.models.company_intelligence import CompanyFact
from app.company_research_source import CompanyResearchSource
from app.company_url import company_base_url


class BasicWebCompanyResearchSource(CompanyResearchSource):
    """
    Lightweight local web research source.

    Retrieves a small set of common public company pages and
    returns only source-backed facts.
    """

    COMMON_PATHS = [
        "/",
        "/about",
        "/customers",
        "/careers",
    ]

    def __init__(self, base_url: str):
        normalized_url = company_base_url(base_url)

        if normalized_url is None:
            raise ValueError(
                "A valid HTTP/HTTPS company or job URL is required."
            )

        self.base_url = normalized_url

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "CareerOS/1.0",
                "Accept": "text/html",
            }
        )

    @staticmethod
    def _clean_text(html: str) -> str:
        text = re.sub(
            r"<script.*?</script>",
            " ",
            html,
            flags=re.S | re.I,
        )
        text = re.sub(
            r"<style.*?</style>",
            " ",
            text,
            flags=re.S | re.I,
        )
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        return unescape(text).strip()

    @staticmethod
    def _extract_page_facts(
        html: str,
        source_url: str,
    ) -> list[CompanyFact]:
        facts: list[CompanyFact] = []

        title_match = re.search(
            r"<title[^>]*>(.*?)</title>",
            html,
            flags=re.I | re.S,
        )

        if title_match:
            title = unescape(
                BasicWebCompanyResearchSource._clean_text(
                    title_match.group(1)
                )
            )

            if title:
                facts.append(
                    CompanyFact(
                        category="page_title",
                        fact=f"Public website title: {title}",
                        source=source_url,
                        confidence="HIGH",
                    )
                )

        description_match = re.search(
            r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']',
            html,
            flags=re.I | re.S,
        )

        if description_match:
            description = unescape(
                description_match.group(1)
            ).strip()

            if description:
                facts.append(
                    CompanyFact(
                        category="product",
                        fact=description,
                        source=source_url,
                        confidence="HIGH",
                    )
                )

        return facts

    def research(self, company: str) -> CompanyResearchResult:
        facts: list[CompanyFact] = []
        visited_urls: set[str] = set()

        for path in self.COMMON_PATHS:
            url = urljoin(
                self.base_url + "/",
                path.lstrip("/"),
            )

            try:
                response = self.session.get(
                    url,
                    timeout=(5, 15),
                    allow_redirects=True,
                )
                response.raise_for_status()
            except requests.RequestException as exc:
                print(
                    f"  Company page unavailable: "
                    f"{url} | {type(exc).__name__}"
                )
                continue

            final_url = response.url

            if final_url in visited_urls:
                continue

            visited_urls.add(final_url)

            page_facts = self._extract_page_facts(
                response.text,
                final_url,
            )

            facts.extend(page_facts)

            final_url_lower = final_url.lower()

            page_text = self._clean_text(
                response.text
            )
            page_text_lower = page_text.lower()

            cs_signal_patterns = {
                r"\bcustomer success\b": "Customer Success",
                r"\bcustomer experience\b": "Customer experience",
                r"\bcustomer adoption\b": "Customer adoption",
                r"\bcustomer health\b": "Customer health",
                r"\bimprov(?:e|es|ing) customer retention\b": "Customer retention",
                r"\bimprov(?:e|es|ing) customer renewals?\b": "Customer renewal",
            }

            for pattern, label in cs_signal_patterns.items():
                if re.search(pattern, page_text_lower):
                    facts.append(
                        CompanyFact(
                            category="cs priority",
                            fact=label,
                            source=final_url,
                            confidence="MEDIUM",
                        )
                    )

            if "/customers" in final_url_lower:
                page_text = self._clean_text(
                    response.text
                )

                customer_signals = [
                    "businesses",
                    "companies",
                    "customers",
                    "startups",
                    "enterprises",
                ]

                matched_signals = [
                    signal
                    for signal in customer_signals
                    if signal in page_text.lower()
                ]

                if matched_signals:
                    facts.append(
                        CompanyFact(
                            category="customer segments",
                            fact=(
                                "The public customers page explicitly "
                                "references customer/business audiences: "
                                + ", ".join(
                                    matched_signals
                                )
                                + "."
                            ),
                            source=final_url,
                            confidence="MEDIUM",
                        )
                    )

        unique_facts: list[CompanyFact] = []
        seen: set[tuple[str, str, str]] = set()
        seen_cs_priorities: set[str] = set()

        for fact in facts:
            normalized_category = fact.category.strip().lower()
            normalized_fact = fact.fact.strip().lower()

            if normalized_category == "cs priority":
                if normalized_fact in seen_cs_priorities:
                    continue

                seen_cs_priorities.add(normalized_fact)

            key = (
                normalized_category,
                normalized_fact,
                fact.source,
            )

            if key not in seen:
                seen.add(key)
                unique_facts.append(fact)

        unique_facts.append(
            CompanyFact(
                category="company_presence",
                fact=(
                    f"Public company pages were retrieved for "
                    f"{company}."
                ),
                source=self.base_url,
                confidence="HIGH",
            )
        )

        unique_facts.append(
            CompanyFact(
                category="research_timestamp",
                fact=(
                    "Research retrieved on "
                    f"{datetime.now(timezone.utc).isoformat()}."
                ),
                source=self.base_url,
                confidence="HIGH",
            )
        )

        return CompanyResearchResult(
            company=company,
            facts=unique_facts,
            research_status="WEB_RESEARCHED",
        )
