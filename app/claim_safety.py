import json
from pathlib import Path

from app.models.claim_safety import (
    ClaimCheck,
    ClaimSafetyResult,
)

from app.claim_fidelity import check_claim_fidelity


BASE_DIR = Path(__file__).resolve().parent.parent

EVIDENCE_FILE = (
    BASE_DIR / "data" / "evidence" / "evidence.json"
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
    """Load the Evidence Library."""

    return load_json(
        EVIDENCE_FILE
    )


def load_strategy(job_id: str):
    """Load Application Strategy."""

    return load_json(
        STRATEGY_DIR
        / f"{job_id}.json"
    )


def build_evidence_index(
    evidence: list[dict]
):
    """Create an Evidence ID lookup."""

    return {
        item["id"]: item
        for item in evidence
    }


def check_forbidden_claim(
    claim: str,
    forbidden_claims: list[str]
):
    """
    Check whether a generated claim contains
    a forbidden claim concept.
    """

    claim_lower = claim.lower()

    for forbidden in forbidden_claims:

        if forbidden.lower() in claim_lower:
            return True, forbidden

    return False, None


def check_claim(
    claim: str,
    evidence_ids: list[str],
    evidence_index: dict,
    forbidden_claims: list[str],
):
    """
    Run the complete claim governance check.

    Checks:

    1. Evidence IDs exist
    2. Evidence is VERIFIED
    3. Forbidden claims are absent
    4. Claim fidelity passes

    Human review remains mandatory.
    """

    # --------------------------------------------------
    # CHECK 1 — Evidence ID supplied
    # --------------------------------------------------

    if not evidence_ids:

        return ClaimCheck(
            claim=claim,
            evidence_ids=[],
            evidence_verified=False,
            forbidden_match=False,
            fidelity_supported=False,
            fidelity_reason=(
                "No Evidence ID supplied."
            ),
            allowed=False,
            reason=(
                "Claim has no supporting Evidence ID."
            ),
            human_review_required=True,
        )

    # --------------------------------------------------
    # CHECK 2 — Evidence IDs exist
    # --------------------------------------------------

    evidence_items = []

    for evidence_id in evidence_ids:

        item = evidence_index.get(
            evidence_id
        )

        if item is None:

            return ClaimCheck(
                claim=claim,
                evidence_ids=evidence_ids,
                evidence_verified=False,
                forbidden_match=False,
                fidelity_supported=False,
                fidelity_reason=(
                    f"Evidence ID {evidence_id} "
                    "does not exist."
                ),
                allowed=False,
                reason=(
                    f"Evidence ID {evidence_id} "
                    "does not exist."
                ),
                human_review_required=True,
            )

        evidence_items.append(item)

    # --------------------------------------------------
    # CHECK 3 — Evidence is verified
    # --------------------------------------------------

    unverified = [
        item["id"]
        for item in evidence_items
        if item["status"] != "VERIFIED"
    ]

    if unverified:

        return ClaimCheck(
            claim=claim,
            evidence_ids=evidence_ids,
            evidence_verified=False,
            forbidden_match=False,
            fidelity_supported=False,
            fidelity_reason=(
                "Evidence is not verified."
            ),
            allowed=False,
            reason=(
                "Claim uses unverified evidence: "
                + ", ".join(unverified)
            ),
            human_review_required=True,
        )

    # --------------------------------------------------
    # CHECK 4 — Forbidden claim detection
    # --------------------------------------------------

    forbidden_match, forbidden_term = (
        check_forbidden_claim(
            claim,
            forbidden_claims
        )
    )

    if forbidden_match:

        return ClaimCheck(
            claim=claim,
            evidence_ids=evidence_ids,
            evidence_verified=True,
            forbidden_match=True,
            fidelity_supported=False,
            fidelity_reason=(
                "Fidelity check not required because "
                "the claim is already forbidden."
            ),
            allowed=False,
            reason=(
                "Claim contains forbidden concept: "
                f"{forbidden_term}"
            ),
            human_review_required=True,
        )

    # --------------------------------------------------
    # CHECK 5 — Claim fidelity
    # --------------------------------------------------

    fidelity = check_claim_fidelity(
        claim,
        evidence_ids
    )

    if not fidelity.supported:

        return ClaimCheck(
            claim=claim,
            evidence_ids=evidence_ids,
            evidence_verified=True,
            forbidden_match=False,
            fidelity_supported=False,
            fidelity_reason=fidelity.reason,
            allowed=False,
            reason=(
                "Claim failed the evidence fidelity "
                "check: "
                + fidelity.reason
            ),
            human_review_required=True,
        )

    # --------------------------------------------------
    # ALL CHECKS PASSED
    # --------------------------------------------------

    return ClaimCheck(
        claim=claim,
        evidence_ids=evidence_ids,
        evidence_verified=True,
        forbidden_match=False,
        fidelity_supported=True,
        fidelity_reason=fidelity.reason,
        allowed=True,
        reason=(
            "Claim passed evidence verification, "
            "forbidden-claim detection and "
            "claim-fidelity checks."
        ),
        human_review_required=True,
    )


def run_safety_gate(
    job_id: str,
    claims: list[dict]
):
    """
    Run the complete Claim Safety Gate.
    """

    evidence = load_evidence()

    strategy = load_strategy(
        job_id
    )

    evidence_index = build_evidence_index(
        evidence
    )

    checks = []

    for claim in claims:

        check = check_claim(
            claim=claim["claim"],
            evidence_ids=claim["evidence_ids"],
            evidence_index=evidence_index,
            forbidden_claims=strategy[
                "forbidden_claims"
            ],
        )

        checks.append(check)

    approved_count = sum(
        1
        for check in checks
        if check.allowed
    )

    blocked_count = sum(
        1
        for check in checks
        if not check.allowed
    )

    return ClaimSafetyResult(
        job_id=job_id,
        total_claims=len(checks),
        approved_claims=approved_count,
        blocked_claims=blocked_count,
        checks=checks,
        all_claims_safe=(
            blocked_count == 0
        ),
        human_review_required=True,
    )


def main():

    print()
    print("=" * 80)
    print("CAREEROS CLAIM GOVERNANCE GATE")
    print("=" * 80)

    # --------------------------------------------------
    # TEST 1 — Legitimate claim
    # --------------------------------------------------

    legitimate_claim = (
        "Managed customer experience performance "
        "through CSAT, SLA, WFM and RCR metrics."
    )

    result_1 = run_safety_gate(
        "JOB-001",
        [
            {
                "claim": legitimate_claim,
                "evidence_ids": ["EV003"],
            }
        ]
    )

    check_1 = result_1.checks[0]

    print()
    print("TEST 1: LEGITIMATE CLAIM")
    print("-" * 80)

    print(
        f"Allowed: "
        f"{check_1.allowed}"
    )

    print(
        f"Evidence verified: "
        f"{check_1.evidence_verified}"
    )

    print(
        f"Fidelity supported: "
        f"{check_1.fidelity_supported}"
    )

    print(
        f"Forbidden match: "
        f"{check_1.forbidden_match}"
    )

    print(
        f"Reason: "
        f"{check_1.reason}"
    )

    # --------------------------------------------------
    # TEST 2 — Obviously fabricated claim
    # --------------------------------------------------

    fabricated_claim = (
        "Managed 50 enterprise SaaS accounts "
        "and increased retention by 35%."
    )

    result_2 = run_safety_gate(
        "JOB-001",
        [
            {
                "claim": fabricated_claim,
                "evidence_ids": ["EV003"],
            }
        ]
    )

    check_2 = result_2.checks[0]

    print()
    print("TEST 2: UNSUPPORTED CLAIM")
    print("-" * 80)

    print(
        f"Allowed: "
        f"{check_2.allowed}"
    )

    print(
        f"Evidence verified: "
        f"{check_2.evidence_verified}"
    )

    print(
        f"Fidelity supported: "
        f"{check_2.fidelity_supported}"
    )

    print(
        f"Forbidden match: "
        f"{check_2.forbidden_match}"
    )

    print(
        f"Reason: "
        f"{check_2.reason}"
    )

    # --------------------------------------------------
    # Final summary
    # --------------------------------------------------

    print()
    print("=" * 80)
    print("CLAIM GOVERNANCE TESTS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
