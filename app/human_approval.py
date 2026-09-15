import json
from pathlib import Path

from app.models.human_approval import HumanApproval
from app.claim_safety import run_safety_gate
from app.tailored_resume import build_tailored_resume


BASE_DIR = Path(__file__).resolve().parent.parent

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


def load_strategy(job_id: str):
    """Load the application strategy."""

    return load_json(
        STRATEGY_DIR
        / f"{job_id}.json"
    )


def prepare_for_approval(job_id: str):
    """
    Prepare a tailored application package
    for human review.

    Nothing is submitted or sent.
    """

    strategy = load_strategy(
        job_id
    )

    resume = build_tailored_resume(
        job_id
    )

    # --------------------------------------------------
    # Collect claims from the generated resume
    # --------------------------------------------------

    claims = []

    for bullet in resume.bullets:

        claims.append(
            {
                "claim": bullet.bullet,
                "evidence_ids": bullet.evidence_ids,
            }
        )

    # --------------------------------------------------
    # Run Claim Safety Gate again
    # --------------------------------------------------

    safety_result = run_safety_gate(
        job_id,
        claims
    )

    claims_safe = (
        safety_result.all_claims_safe
    )

    # --------------------------------------------------
    # Determine package readiness
    # --------------------------------------------------

    resume_ready = (
        len(resume.bullets) > 0
        and claims_safe
    )

    cover_letter_ready = (
        strategy["cover_letter"]
        in [
            "RECOMMENDED",
            "OPTIONAL"
        ]
    )

    outreach_ready = (
        strategy["networking"]
        in [
            "RECOMMENDED",
            "HIGHLY RECOMMENDED"
        ]
    )

    return HumanApproval(
        job_id=job_id,
        company=resume.company,
        title=resume.title,
        resume_ready=resume_ready,
        cover_letter_ready=cover_letter_ready,
        outreach_ready=outreach_ready,
        claims_safe=claims_safe,
        decision="PENDING",
        reviewer_notes=None,
        approved_by_human=False,
    )


def display_approval_request(
    approval: HumanApproval
):
    """Display the package awaiting human approval."""

    print()
    print("=" * 80)
    print("CAREEROS HUMAN APPROVAL GATE")
    print("=" * 80)

    print()
    print(f"Company: {approval.company}")
    print(f"Role: {approval.title}")

    print()
    print("APPLICATION PACKAGE")
    print("-" * 80)

    print(
        f"Resume ready: "
        f"{approval.resume_ready}"
    )

    print(
        f"Cover letter ready: "
        f"{approval.cover_letter_ready}"
    )

    print(
        f"Outreach ready: "
        f"{approval.outreach_ready}"
    )

    print()
    print("CLAIM GOVERNANCE")
    print("-" * 80)

    print(
        f"All claims safe: "
        f"{approval.claims_safe}"
    )

    print()
    print("HUMAN DECISION")
    print("-" * 80)

    print(
        f"Decision: "
        f"{approval.decision}"
    )

    print(
        f"Approved by human: "
        f"{approval.approved_by_human}"
    )

    print()
    print("=" * 80)


def main():

    approval = prepare_for_approval(
        "JOB-001"
    )

    display_approval_request(
        approval
    )


if __name__ == "__main__":
    main()
