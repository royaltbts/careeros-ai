import json

from app.models.job_discovery import JobDiscovery
from app.models.career_strategy import CareerStrategy


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_jobs(path: str) -> list[JobDiscovery]:
    data = load_json(path)
    return [JobDiscovery.model_validate(item) for item in data]


def load_strategy(path: str) -> CareerStrategy:
    data = load_json(path)
    return CareerStrategy.model_validate(data)


def is_relevant_job(
    job: JobDiscovery,
    strategy: CareerStrategy
) -> bool:

    title = job.title.lower()

    for target_role in strategy.target_roles:
        if target_role.lower() in title:
            return True

    if "customer success" in title:
        return True

    return False


def scout_jobs(
    jobs: list[JobDiscovery],
    strategy: CareerStrategy
) -> list[JobDiscovery]:

    relevant_jobs = []

    for job in jobs:
        if is_relevant_job(job, strategy):
            relevant_jobs.append(job)

    return relevant_jobs


if __name__ == "__main__":

    jobs = load_jobs(
        "data/jobs/discovered_jobs.json"
    )

    strategy = load_strategy(
        "data/candidate/career_strategy.json"
    )

    relevant_jobs = scout_jobs(
        jobs,
        strategy
    )

    print()
    print("=" * 70)
    print("CAREEROS MARKET SCOUT")
    print("=" * 70)

    print(f"Jobs discovered: {len(jobs)}")
    print(f"Relevant jobs: {len(relevant_jobs)}")
    print()

    for job in relevant_jobs:
        print(
            f"{job.job_id}: "
            f"{job.title} — "
            f"{job.company}"
        )

    print("=" * 70)
