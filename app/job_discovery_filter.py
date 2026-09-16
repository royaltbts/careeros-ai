from app.job_location import evaluate_location
from app.models.career_strategy import CareerStrategy
from app.models.job_discovery import JobDiscovery


def filter_by_strategy(
    jobs: list[JobDiscovery],
    strategy: CareerStrategy,
) -> list[JobDiscovery]:
    eligible_jobs = []

    for job in jobs:
        result = evaluate_location(
            job.location,
            job.work_mode,
            strategy,
        )

        if result.eligible:
            eligible_jobs.append(job)

    return eligible_jobs
