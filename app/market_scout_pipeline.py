import json
from pathlib import Path

from app.models.job_discovery import JobDiscovery
from app.models.job_intelligence import JobIntelligence
from app.models.job import JobRequirement


INPUT_FILE = "data/jobs/discovered_jobs.json"
OUTPUT_DIR = Path("data/jobs/intelligence")


def load_discovered_jobs(path: str) -> list[JobDiscovery]:
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return [
        JobDiscovery.model_validate(item)
        for item in data
    ]


def classify_requirement(name: str) -> tuple[str, str]:

    name_lower = name.lower()

    critical_terms = [
        "advanced sql",
        "snowflake",
        "technical integrations",
        "deep saas",
        "power bi development"
    ]

    preferred_terms = [
        "crm",
        "customer success platform"
    ]

    for term in critical_terms:
        if term in name_lower:
            return "CRITICAL", "TOOLS"

    for term in preferred_terms:
        if term in name_lower:
            return "PREFERRED", "TOOLS"

    return "CORE", "CUSTOMER_SUCCESS"


def build_job_intelligence(
    job: JobDiscovery
) -> JobIntelligence:

    description = job.raw_description
    description_lower = description.lower()

    requirements = []

    requirement_candidates = [
        "Customer relationship management",
        "Customer satisfaction",
        "Business reviews",
        "Customer health",
        "Customer adoption",
        "Escalation management",
        "Stakeholder management",
        "Customer communication",
        "Problem solving",
        "People leadership",
        "Continuous improvement",
        "Advanced SQL",
        "Snowflake",
        "Power BI development",
        "Technical integrations",
        "SaaS experience",
        "CRM experience",
        "Customer Success platform experience"
    ]

    for requirement in requirement_candidates:

        if requirement.lower() in description_lower:

            criticality, category = classify_requirement(
                requirement
            )

            requirements.append(
                JobRequirement(
                    name=requirement,
                    criticality=criticality,
                    category=category
                )
            )

    customer_success_capabilities = []

    capability_terms = [
        "Customer relationship management",
        "Customer satisfaction",
        "Business reviews",
        "Customer health",
        "Customer adoption",
        "Escalation management",
        "Customer communication",
        "Problem solving",
        "People leadership",
        "Continuous improvement"
    ]

    for capability in capability_terms:

        if capability.lower() in description_lower:
            customer_success_capabilities.append(
                capability
            )

    tools_and_platforms = []

    tool_terms = [
        "CRM",
        "Customer Success platform",
        "Advanced SQL",
        "Snowflake",
        "Power BI",
        "Technical integrations"
    ]

    for tool in tool_terms:

        if tool.lower() in description_lower:
            tools_and_platforms.append(tool)

    return JobIntelligence(
        job_id=job.job_id,
        company=job.company,
        title=job.title,
        location=job.location,
        source_url=job.source_url,
        source_type=job.source,
        employment_type=None,
        industry=None,
        experience_required=None,
        responsibilities=[],
        requirements=requirements,
        customer_success_capabilities=customer_success_capabilities,
        tools_and_platforms=tools_and_platforms
    )


def save_job_intelligence(
    intelligence: JobIntelligence
):
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        OUTPUT_DIR
        / f"{intelligence.job_id}.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            intelligence.model_dump(),
            file,
            indent=2,
            ensure_ascii=False
        )

    return output_file


def main():

    jobs = load_discovered_jobs(
        INPUT_FILE
    )

    print()
    print("=" * 70)
    print("CAREEROS MARKET SCOUT → JOB INTELLIGENCE")
    print("=" * 70)

    for job in jobs:

        intelligence = build_job_intelligence(
            job
        )

        output_file = save_job_intelligence(
            intelligence
        )

        print()
        print(
            f"{job.job_id}: "
            f"{job.title} — "
            f"{job.company}"
        )

        print(
            f"Requirements: "
            f"{len(intelligence.requirements)}"
        )

        print(
            f"Saved: "
            f"{output_file}"
        )

    print()
    print("=" * 70)
    print("JOB INTELLIGENCE PERSISTENCE: COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
