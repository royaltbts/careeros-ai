from datetime import datetime, timezone

import requests

from app.job_discovery_provider import JobDiscoveryProvider
from app.models.job_discovery import JobDiscovery


class WebJobDiscoveryProvider(JobDiscoveryProvider):
    def __init__(self, url: str, source: str = "Web"):
        self.url = url
        self.source = source

    def discover(self) -> list[JobDiscovery]:
        response = requests.get(
            self.url,
            timeout=20,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/140.0 Safari/537.36"
                )
            },
        )
        response.raise_for_status()

        discovered_at = datetime.now(
            timezone.utc
        ).date().isoformat()

        return [
            JobDiscovery(
                job_id=f"WEB-{abs(hash(self.url))}",
                company="Unknown",
                title="Unknown Customer Success Role",
                location=None,
                source=self.source,
                source_url=self.url,
                discovered_at=discovered_at,
                raw_description=response.text,
            )
        ]
