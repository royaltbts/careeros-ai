from datetime import datetime, timezone
from html import unescape
import re

import requests

from app.job_discovery_provider import JobDiscoveryProvider
from app.models.job_discovery import JobDiscovery
from app.job_work_mode import detect_work_mode


class GreenhouseJobDiscoveryProvider(JobDiscoveryProvider):
    def __init__(
        self,
        board_token: str,
        role_keywords: list[str] | None = None,
    ):
        self.board_token = board_token.strip()
        self.role_keywords = [
            keyword.lower()
            for keyword in (
                role_keywords
                or [
                    "customer success",
                    "customer success manager",
                    "strategic customer success",
                    "enterprise customer success",
                    "customer experience",
                ]
            )
        ]

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "CareerOS/1.0",
                "Accept": "application/json",
            }
        )

    def _get(self, url: str) -> dict | None:
        try:
            response = self.session.get(
                url,
                timeout=(5, 15),
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            print(
                f"  Greenhouse request failed: "
                f"{url} | {type(exc).__name__}"
            )
            return None

    @staticmethod
    def _clean_html(value: str) -> str:
        text = unescape(value or "")
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def discover(self) -> list[JobDiscovery]:
        if not self.board_token:
            raise ValueError("Greenhouse board token cannot be empty.")

        list_url = (
            "https://boards-api.greenhouse.io/v1/boards/"
            f"{self.board_token}/jobs"
        )

        listing = self._get(list_url)
        if listing is None:
            return []

        jobs = listing.get("jobs", [])

        discovered_at = datetime.now(
            timezone.utc
        ).date().isoformat()

        results: list[JobDiscovery] = []

        for job in jobs:
            title = (job.get("title") or "").strip()
            title_lower = title.lower()

            if not any(
                keyword in title_lower
                for keyword in self.role_keywords
            ):
                continue

            job_id = str(job.get("id", "")).strip()

            if not job_id:
                continue

            detail_url = (
                "https://boards-api.greenhouse.io/v1/boards/"
                f"{self.board_token}/jobs/{job_id}"
            )

            detail = self._get(detail_url)

            if detail is None:
                continue

            location = (
                detail.get("location", {}).get("name")
                or job.get("location", {}).get("name")
            )

            description = self._clean_html(
                detail.get("content", "")
            )

            work_mode = detect_work_mode(description)

            source_url = (
                detail.get("absolute_url")
                or job.get("absolute_url")
            )

            company = (
                detail.get("company_name")
                or job.get("company_name")
                or self.board_token
            )

            results.append(
                JobDiscovery(
                    job_id=f"GH-{self.board_token}-{job_id}",
                    company=company,
                    title=title,
                    location=location,
                    source="Greenhouse",
                    source_url=source_url,
                    discovered_at=discovered_at,
                    raw_description=description,
                    work_mode=work_mode,
                )
            )

        return results
