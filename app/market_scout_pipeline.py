import json
import re
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



def _extract_sections(description: str) -> dict[str, list[str]]:
    """Extract common job-description sections from line-preserved text."""

    headings = {
        "responsibilities": "responsibilities",
        "responsibility": "responsibilities",
        "what you'll do": "responsibilities",
        "what you’ll do": "responsibilities",
        "requirements": "requirements",
        "requirement": "requirements",
        "qualifications": "requirements",
        "qualification": "requirements",
        "what you'll need": "requirements",
        "what you’ll need": "requirements",
        "who you are": "requirements",
        "nice to haves": "requirements",
    }

    sections: dict[str, list[str]] = {}
    current_section: str | None = None

    for raw_line in description.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        normalized = line.rstrip(":").strip().lower()

        if normalized in headings:
            current_section = headings[normalized]
            sections.setdefault(current_section, [])
            continue

        if current_section is None:
            continue

        line = re.sub(r"^[•*\-\u2022]\s*", "", line)
        line = re.sub(r"^\d+[.)]\s*", "", line)

        if line:
            sections[current_section].append(line)

    return sections


def _canonical_requirements(requirement_lines: list[str]) -> list[str]:
    """Map requirement signals to the canonical CareerOS vocabulary."""

    signals = {
        "Customer relationship management": [
            "customer relationship",
            "account relationship",
        ],
        "Customer satisfaction": [
            "customer satisfaction",
        ],
        "Business reviews": [
            "business review",
        ],
        "Customer health": [
            "customer health",
        ],
        "Customer adoption": [
            "customer adoption",
        ],
        "Escalation management": [
            "escalation management",
            "manage escalations",
        ],
        "Stakeholder management": [
            "stakeholder management",
            "executive sponsor",
            "key relationships",
        ],
        "Customer communication": [
            "customer communication",
            "communication skills",
        ],
        "Problem solving": [
            "problem solving",
            "solve customer problems",
        ],
        "People leadership": [
            "people management",
            "people leadership",
            "hiring",
            "hire, train, and coach",
            "hiring, training, and coaching",
        ],
        "Continuous improvement": [
            "continuous improvement",
        ],
        "Advanced SQL": [
            "advanced sql",
        ],
        "Snowflake": [
            "snowflake",
        ],
        "Power BI development": [
            "power bi development",
        ],
        "Technical integrations": [
            "technical integrations",
        ],
        "SaaS experience": [
            "saas",
            "software products",
            "software company",
        ],
        "CRM experience": [
            "crm",
        ],
        "Customer Success platform experience": [
            "customer success platform",
        ],
    }

    normalized_lines = [
        line.replace("&nbsp;", " ").strip().lower()
        for line in requirement_lines
    ]

    results = []

    for canonical_name, keywords in signals.items():
        if any(
            keyword in line
            for line in normalized_lines
            for keyword in keywords
        ):
            results.append(canonical_name)

    return results


def _extract_experience(description: str) -> str | None:
    """Extract the specific experience requirement containing years."""

    matches = re.findall(
        r"[^.\n]*\b\d+\+?\s+years?\b[^.\n]*",
        description,
        re.IGNORECASE,
    )

    if not matches:
        return None

    return " ".join(
        match.strip()
        for match in matches
    )

def build_job_intelligence(
    job: JobDiscovery
) -> JobIntelligence:

    description = job.raw_description
    description_lower = description.lower()
    sections = _extract_sections(description)
    responsibilities = [
        item.replace("&nbsp;", " ").strip()
        for item in sections.get("responsibilities", [])
        if item.replace("&nbsp;", " ").strip()
        and item.strip().lower() != "you will:"
        and not item.strip().lower().startswith("we are seeking a manager to lead")
    ]

    experience_required = _extract_experience(description)

    requirements = []

    requirement_lines = sections.get("requirements", [])
    requirement_candidates = _canonical_requirements(
        requirement_lines
    )

    for requirement in requirement_candidates:
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
        experience_required=experience_required,
        responsibilities=responsibilities,
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
