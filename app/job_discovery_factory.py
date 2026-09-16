import os

from app.job_discovery_local import LocalJobDiscoveryProvider
from app.job_discovery_greenhouse import GreenhouseJobDiscoveryProvider
from app.models.job_discovery import JobDiscovery
from app.models.career_strategy import CareerStrategy
from app.job_discovery_filter import filter_by_strategy


def discover_jobs(
    local_path: str,
    strategy: CareerStrategy | None = None,
) -> tuple[list[JobDiscovery], str]:
    provider_name = os.getenv(
        "CAREEROS_DISCOVERY_PROVIDER",
        "local",
    ).strip().lower()

    if provider_name == "local":
        provider = LocalJobDiscoveryProvider(local_path)
        return provider.discover(), "LOCAL"

    if provider_name == "greenhouse":
        boards = [
            board.strip()
            for board in os.getenv(
                "CAREEROS_GREENHOUSE_BOARDS",
                "",
            ).split(",")
            if board.strip()
        ]

        if not boards:
            raise ValueError(
                "CAREEROS_GREENHOUSE_BOARDS must contain "
                "at least one Greenhouse board token."
            )

        jobs: list[JobDiscovery] = []

        for board in boards:
            provider = GreenhouseJobDiscoveryProvider(board)
            jobs.extend(provider.discover())


        if strategy is not None:
            jobs = filter_by_strategy(
                jobs,
                strategy,
            )
        return jobs, "GREENHOUSE"

    raise ValueError(
        f"Unsupported CAREEROS_DISCOVERY_PROVIDER: {provider_name}"
    )
