import json
from pathlib import Path

from app.models.application_strategy import ApplicationStrategy
from app.models.evidence import EvidenceItem
from app.evidence_matcher import match_requirement


BASE_DIR = Path(__file__).resolve().parent.parent

RANKING_FILE = BASE_DIR / "data" / "jobs" / "ranked_opportunities.json"
EVIDENCE_FILE = BASE_DIR / "data" / "evidence" / "evidence.json"
INTELLIGENCE_DIR = BASE_DIR / "data" / "jobs" / "intelligence"
OUTPUT_DIR = BASE_DIR / "data" / "jobs" / "strategies"


def load_json(path: Path):
    """Load JSON data from a file."""
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_evidence() -> list[EvidenceItem]:
    """Load and validate the Evidence Library."""
    data = load_json(EVIDENCE_FILE)

    return [
        EvidenceItem.model_validate(item)
        for item in data
    ]


def load_ranked_opportunities() -> list[dict]:
    """Load ranked job opportunities."""
    data = load_json(RANKING_FILE)

    return data["opportunities"]


def load_job_intelligence(job_id: str) -> dict:
    """Load Job Intelligence for a specific job."""
    intelligence_file = (
        INTELLIGENCE_DIR / f"{job_id}.json"
    )

    return load_json(intelligence_file)


def load_company_intelligence(job_id: str) -> dict:
    """Load persisted Company Intelligence for a job."""
    company_file = (
        BASE_DIR
        / "data"
        / "jobs"
        / "company_intelligence"
        / f"{job_id}.json"
    )

    if not company_file.exists():
        return {}

    return load_json(company_file)


def build_evidence_map(
    opportunity: dict,
    evidence: list[EvidenceItem]
):
    """
    Match job requirements against verified candidate evidence.

    Uses the Evidence Matcher so requirement-to-evidence
    matching can use both lexical and capability-aware
    retrieval.

    Only VERIFIED evidence is eligible.

    DIRECT evidence strengthens the candidate's evidence
    profile.

    TRANSFERABLE evidence is recorded separately and must
    never be presented as direct experience.

    WEAK and NO_MATCH results are not treated as evidence
    strengths.
    """
    evidence_strengths = []
    transferable_capabilities = []

    intelligence = load_job_intelligence(
        opportunity["job_id"]
    )

    requirements = intelligence.get(
        "requirements",
        []
    )

    for requirement in requirements:
        requirement_name = (
            requirement["name"]
            .strip()
        )

        matches = match_requirement(
            requirement_name,
            evidence
        )

        for match in matches:
            if match.match_type == "DIRECT":
                evidence_item = next(
                    (
                        item
                        for item in evidence
                        if item.id == match.evidence_id
                        and item.status == "VERIFIED"
                    ),
                    None
                )

                if evidence_item is not None:
                    evidence_strengths.append(
                        evidence_item.capability
                    )

                break

            if match.match_type == "TRANSFERABLE":
                evidence_item = next(
                    (
                        item
                        for item in evidence
                        if item.id == match.evidence_id
                        and item.status == "VERIFIED"
                    ),
                    None
                )

                if evidence_item is not None:
                    transferable_capabilities.append(
                        evidence_item.capability
                    )

                break

    return (
        sorted(set(evidence_strengths)),
        sorted(set(transferable_capabilities))
    )

def determine_forbidden_claims(
    opportunity: dict
) -> list[str]:
    """
    Claims that CareerOS must never present as
    established candidate experience.

    This is intentionally conservative.
    """

    forbidden_claims = [
        "SaaS experience",
        "Advanced SQL",
        "Snowflake",
        "Power BI development",
        "Jira administration",
        "Confluence administration",
        "CRM expertise",
        "Customer Success platform expertise",
        "Enterprise account ownership"
    ]

    return forbidden_claims


def determine_application_decision(
    opportunity: dict,
    company_intelligence: dict | None = None
) -> str:
    """Determine the application recommendation.

    Company Intelligence is available for decision support,
    while human approval remains a separate mandatory control.
    """

    company_intelligence = company_intelligence or {}

    if opportunity["critical_gaps"]:
        return "CONDITIONAL"

    if opportunity["priority"] == "HIGH":
        return "YES"

    return "REVIEW"

def determine_resume_tailoring(
    priority: str
) -> str:
    """Determine resume tailoring requirement."""

    if priority == "HIGH":
        return "REQUIRED"

    if priority == "MEDIUM":
        return "RECOMMENDED"

    return "NOT REQUIRED"


def determine_cover_letter(
    priority: str
) -> str:
    """Determine cover-letter recommendation."""

    if priority == "HIGH":
        return "RECOMMENDED"

    if priority == "MEDIUM":
        return "OPTIONAL"

    return "NOT REQUIRED"


def determine_networking(
    priority: str,
    critical_gaps: list[str]
) -> str:
    """Determine networking recommendation."""

    if critical_gaps:
        return "HIGHLY RECOMMENDED"

    if priority in ["HIGH", "MEDIUM"]:
        return "RECOMMENDED"

    return "OPTIONAL"


def build_strategy(
    opportunity: dict,
    evidence: list[EvidenceItem]
) -> ApplicationStrategy:
    """Build the Application Strategy for one opportunity."""

    (
        evidence_strengths,
        transferable_capabilities
    ) = build_evidence_map(
        opportunity,
        evidence
    )

    priority = opportunity["priority"]

    company_intelligence = load_company_intelligence(
        opportunity["job_id"]
    )

    company_strategic_fit = (
        company_intelligence.get(
            "strategic_relevance",
            ""
        )
    )

    company_risks = company_intelligence.get(
        "potential_risks",
        []
    )

    company_research_status = (
        company_intelligence.get(
            "research_status",
            "NOT_RESEARCHED"
        )
    )

    company_intelligence_review_required = (
        company_intelligence.get(
            "human_review_required",
            True
        )
    )

    resume_tailoring = determine_resume_tailoring(
        priority
    )

    cover_letter = determine_cover_letter(
        priority
    )

    networking = determine_networking(
        priority,
        opportunity["critical_gaps"]
    )

    application_decision = determine_application_decision(
        opportunity,
        company_intelligence
    )

    strategy = ApplicationStrategy(
        job_id=opportunity["job_id"],
        company=opportunity["company"],
        title=opportunity["title"],

        priority=priority,

        fit_score=opportunity["fit_score"],

        opportunity_score=opportunity[
            "opportunity_score"
        ],

        application_decision=application_decision,

        resume_tailoring=resume_tailoring,

        cover_letter=cover_letter,

        networking=networking,

        evidence_strengths=evidence_strengths,

        transferable_capabilities=(
            transferable_capabilities
        ),

        critical_gaps=opportunity[
            "critical_gaps"
        ],

        core_gaps=opportunity[
            "core_gaps"
        ],

        forbidden_claims=(
            determine_forbidden_claims(
                opportunity
            )
        ),
        company_strategic_fit=company_strategic_fit,
        company_risks=company_risks,
        company_research_status=company_research_status,
        company_intelligence_review_required=(
            company_intelligence_review_required
        ),

        # External actions must always require
        # explicit human approval.
        human_approval_required=True
    )

    return strategy


def save_strategy(
    strategy: ApplicationStrategy
):
    """Save Application Strategy as JSON."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        OUTPUT_DIR
        / f"{strategy.job_id}.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            strategy.model_dump(),
            file,
            indent=2,
            ensure_ascii=False
        )

    return output_file


def main():

    opportunities = load_ranked_opportunities()

    evidence = load_evidence()

    print()
    print("=" * 80)
    print("CAREEROS APPLICATION STRATEGY")
    print("=" * 80)

    for opportunity in opportunities:

        strategy = build_strategy(
            opportunity,
            evidence
        )

        output_file = save_strategy(
            strategy
        )

        print()

        print(
            f"{strategy.job_id}: "
            f"{strategy.title}"
        )

        print(
            f"Priority: "
            f"{strategy.priority}"
        )

        print(
            f"Fit: "
            f"{strategy.fit_score:.2f}"
        )

        print(
            f"Opportunity: "
            f"{strategy.opportunity_score:.2f}"
        )

        print(
            f"Application: "
            f"{strategy.application_decision}"
        )

        print(
            f"Evidence strengths: "
            f"{len(strategy.evidence_strengths)}"
        )

        print(
            f"Transferable capabilities: "
            f"{len(strategy.transferable_capabilities)}"
        )

        print(
            f"Critical gaps: "
            f"{len(strategy.critical_gaps)}"
        )

        print(
            f"Core gaps: "
            f"{len(strategy.core_gaps)}"
        )

        print(
            f"Resume: "
            f"{strategy.resume_tailoring}"
        )

        print(
            f"Networking: "
            f"{strategy.networking}"
        )

        print(
            f"Human approval: "
            f"{strategy.human_approval_required}"
        )

        print(
            f"Saved: "
            f"{output_file}"
        )

    print()
    print("=" * 80)
    print("APPLICATION STRATEGIES: COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
