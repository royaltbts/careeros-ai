import json

from app.job_discovery_provider import JobDiscoveryProvider
from app.models.job_discovery import JobDiscovery


class LocalJobDiscoveryProvider(JobDiscoveryProvider):
    def __init__(self, path: str):
        self.path = path

    def discover(self) -> list[JobDiscovery]:
        with open(self.path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return [
            JobDiscovery.model_validate(item)
            for item in data
        ]
