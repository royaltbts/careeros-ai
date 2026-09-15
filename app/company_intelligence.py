import json
from pathlib import Path

from app.models.company_intelligence import CompanyIntelligence


INTELLIGENCE_DIR = Path("data/jobs/intelligence")
COMPANY_INTELLIGENCE_DIR = Path("data/jobs/company_intelligence")


RESEARCH_QUALITY = {
    "NOT_RESEARCHED": 0,
    "MOCK": 1,
    "ROLE_DERIVED": 2,
    "WEB_RESEARCHED": 3,
}


def research_quality(status: str) -> int:
    """Return the relative quality of a research provenance status."""
    return RESEARCH_QUALITY.get(
        status.strip().upper(),
        0,
    )


def load_job_intelligence(job_id: str) -> dict:
    path = INTELLIGENCE_DIR / f"{job_id}.json"

    if not path.exists():
        raise FileNotFoundError(
            f"Job intelligence not found: {path}"
        )

    return json.loads(path.read_text())


def build_company_intelligence(job_id: str) -> CompanyIntelligence:
    job = load_job_intelligence(job_id)

    priorities = job.get(
        "customer_success_capabilities",
        [],
    )

    requirements = job.get(
        "requirements",
        [],
    )

    likely_priorities = []

    for priority in priorities:
        if priority not in likely_priorities:
            likely_priorities.append(priority)

    facts = []

    if priorities:
        facts.append(
            {
                "category": "CS Priorities",
                "fact": (
                    "The role emphasizes: "
                    + ", ".join(priorities)
                ),
                "source": job.get(
                    "source_url",
                    "Job intelligence",
                ),
                "confidence": "HIGH",
            }
        )

    if requirements:
        facts.append(
            {
                "category": "Role Requirements",
                "fact": (
                    f"The role contains "
                    f"{len(requirements)} structured requirements."
                ),
                "source": job.get(
                    "source_url",
                    "Job intelligence",
                ),
                "confidence": "HIGH",
            }
        )

    strategic_relevance = ""

    if likely_priorities:
        strategic_relevance = (
            "The company's role requirements show "
            "clear emphasis on Customer Success capabilities: "
            + ", ".join(likely_priorities)
            + "."
        )

    intelligence = CompanyIntelligence(
        company=job["company"],
        customer_success_model=None,
        likely_cs_priorities=likely_priorities,
        strategic_relevance=strategic_relevance,
        facts=facts,
        research_status="ROLE_DERIVED",
        human_review_required=True,
    )

    return intelligence


def save_company_intelligence(
    intelligence: CompanyIntelligence,
    job_id: str,
) -> Path:
    COMPANY_INTELLIGENCE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = (
        COMPANY_INTELLIGENCE_DIR
        / f"{job_id}.json"
    )

    if path.exists():
        existing = CompanyIntelligence.model_validate(
            json.loads(path.read_text())
        )

        existing_quality = research_quality(
            existing.research_status
        )
        new_quality = research_quality(
            intelligence.research_status
        )

        if new_quality < existing_quality:
            return path

    path.write_text(
        json.dumps(
            intelligence.model_dump(),
            indent=2,
        )
    )

    return path
