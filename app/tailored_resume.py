import json
from pathlib import Path

from app.models.tailored_resume import (
    TailoredResume,
    ResumeBullet,
)

from app.models.evidence_map import EvidenceMapping

from app.claim_safety import run_safety_gate
from app.evidence_matcher import match_requirement
from app.models.evidence import EvidenceItem


BASE_DIR = Path(__file__).resolve().parent.parent

EVIDENCE_FILE = (
    BASE_DIR / "data" / "evidence" / "evidence.json"
)

INTELLIGENCE_DIR = (
    BASE_DIR / "data" / "jobs" / "intelligence"
)

STRATEGY_DIR = (
    BASE_DIR / "data" / "jobs" / "strategies"
)


def load_json(path: Path):
    """Load JSON from a file."""

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def load_evidence():
    """Load the verified Evidence Library."""

    return load_json(
        EVIDENCE_FILE
    )


def load_job_intelligence(job_id: str):
    """Load Job Intelligence."""

    return load_json(
        INTELLIGENCE_DIR
        / f"{job_id}.json"
    )


def load_strategy(job_id: str):
    """Load Application Strategy."""

    return load_json(
        STRATEGY_DIR
        / f"{job_id}.json"
    )


def find_evidence(
    evidence_id: str,
    evidence: list[dict]
):
    """Find one evidence item by ID."""

    for item in evidence:
        if item["id"] == evidence_id:
            return item

    return None


def build_resume_bullet(
    requirement: str,
    evidence_item: dict
):
    """
    Convert verified evidence into a conservative
    job-oriented resume bullet.

    This does not invent metrics, tools, customers,
    account ownership or outcomes.
    """

    evidence_id = evidence_item["id"]

    if evidence_id == "EV003":

        bullet = (
            "Managed customer experience performance "
            "through CSAT, SLA, WFM and RCR metrics."
        )

    elif evidence_id == "EV001":

        bullet = (
            "Conducted weekly business reviews and "
            "monthly process-excellence reviews involving "
            "metrics, performance discussions and "
            "stakeholder communication."
        )

    elif evidence_id == "EV004":

        bullet = (
            "Applied continuous improvement by reorganizing "
            "the knowledge base and implementing "
            "issue-category-based bots to address recurring "
            "customer issues and protect SLA."
        )

    elif evidence_id == "EV002":

        bullet = (
            "Handled customer-related operational issues "
            "including Google Play, gift card, refund and "
            "Pixel handset-related issues."
        )

    elif evidence_id == "EV005":

        bullet = (
            "Led teams and managed operational performance "
            "within an operations leadership environment."
        )

    elif evidence_id == "EV006":

        bullet = (
            "Managed process improvement projects involving "
            "stakeholder communication and implementation."
        )

    else:

        bullet = evidence_item["claim"]

    return bullet


def build_tailored_resume(
    job_id: str
):
    """
    Build an evidence-grounded tailored resume
    for one job.

    Every generated resume claim passes through
    the Claim Safety Gate before being included.
    """

    intelligence = load_job_intelligence(
        job_id
    )

    strategy = load_strategy(
        job_id
    )

    evidence = load_evidence()

    bullets = []

    # --------------------------------------------------
    # Build bullets from job requirements
    # --------------------------------------------------

    for requirement in intelligence["requirements"]:
        requirement_name = (
            requirement["name"]
        )

        evidence_items = [
            EvidenceItem.model_validate(item)
            for item in evidence
            if item["status"] == "VERIFIED"
        ]

        matches = match_requirement(
            requirement_name,
            evidence_items,
        )

        # Prefer DIRECT evidence.
        direct_matches = [
            match
            for match in matches
            if match.match_type == "DIRECT"
        ]

        transferable_matches = [
            match
            for match in matches
            if match.match_type == "TRANSFERABLE"
        ]

        selected_match = None
        evidence_type = None
        confidence = None

        if direct_matches:
            selected_match = direct_matches[0]
            evidence_type = "DIRECT"
            confidence = "HIGH"
        elif transferable_matches:
            selected_match = transferable_matches[0]
            evidence_type = "TRANSFERABLE"
            confidence = "MEDIUM"

        if selected_match is None:
            continue

        matched_item = find_evidence(
            selected_match.evidence_id,
            evidence,
        )

        if matched_item is None:
            continue

        bullet = build_resume_bullet(
            requirement_name,
            matched_item
        )

        # Claim Safety Gate
        # --------------------------------------------------

        safety_result = run_safety_gate(
            job_id,
            [
                {
                    "claim": bullet,
                    "evidence_ids": [
                        matched_item["id"]
                    ],
                }
            ]
        )

        safety_check = safety_result.checks[0]

        # --------------------------------------------------
        # Block unsafe claims
        # --------------------------------------------------

        if not safety_check.allowed:

            print()
            print("BLOCKED CLAIM")
            print("-" * 80)
            print(
                f"Requirement: "
                f"{requirement_name}"
            )
            print(
                f"Claim: "
                f"{bullet}"
            )
            print(
                f"Reason: "
                f"{safety_check.reason}"
            )
            print("-" * 80)

            continue

        # --------------------------------------------------
        # Add only approved claims
        # --------------------------------------------------

        bullets.append(
            ResumeBullet(
                requirement=requirement_name,
                bullet=bullet,
                evidence_ids=[
                    matched_item["id"]
                ],
                confidence=confidence,
                allowed=True,
                human_review_required=True,
            )
        )

    # --------------------------------------------------
    # Positioning
    # --------------------------------------------------

    headline = (
        "Customer Success | Customer Experience | "
        "Operations & Continuous Improvement"
    )

    summary = (
        "Customer-focused operations leader with "
        "experience in customer communication, business "
        "reviews, customer experience metrics, people "
        "leadership, project management and continuous "
        "improvement."
    )

    # --------------------------------------------------
    # Missing requirements
    # --------------------------------------------------

    generated_requirements = {
        bullet.requirement
        for bullet in bullets
    }

    missing_requirements = [
        requirement["name"]
        for requirement in intelligence["requirements"]
        if requirement["name"]
        not in generated_requirements
    ]

    # --------------------------------------------------
    # Build final TailoredResume object
    # --------------------------------------------------

    return TailoredResume(
        job_id=job_id,
        company=intelligence["company"],
        title=intelligence["title"],
        headline=headline,
        summary=summary,
        bullets=bullets,
        excluded_claims=strategy[
            "forbidden_claims"
        ],
        human_review_required=True,
    )


def main():

    print()
    print("=" * 80)
    print("CAREEROS TAILORED RESUME")
    print("=" * 80)

    job_id = "JOB-001"

    resume = build_tailored_resume(
        job_id
    )

    print()
    print(
        f"Company: "
        f"{resume.company}"
    )

    print(
        f"Role: "
        f"{resume.title}"
    )

    print()
    print("HEADLINE")
    print("-" * 80)
    print(resume.headline)

    print()
    print("SUMMARY")
    print("-" * 80)
    print(resume.summary)

    print()
    print("RESUME BULLETS")
    print("-" * 80)

    for bullet in resume.bullets:

        print()
        print(
            f"Requirement: "
            f"{bullet.requirement}"
        )

        print(
            f"Evidence: "
            f"{bullet.evidence_ids}"
        )

        print(
            f"Confidence: "
            f"{bullet.confidence}"
        )

        print(
            f"Allowed: "
            f"{bullet.allowed}"
        )

        print(
            f"Human review: "
            f"{bullet.human_review_required}"
        )

        print(
            f"Bullet: "
            f"{bullet.bullet}"
        )

    print()
    print("EXCLUDED CLAIMS")
    print("-" * 80)

    for claim in resume.excluded_claims:
        print(f"- {claim}")

    print()
    print(
        f"Human approval required: "
        f"{resume.human_review_required}"
    )

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
