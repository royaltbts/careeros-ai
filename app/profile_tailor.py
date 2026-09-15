import json
from pathlib import Path

from app.models.profile_tailor import (
    ProfileTailorOutput,
    TailoredClaim,
)
from app.models.evidence_map import EvidenceMapping
from app.models.evidence import EvidenceItem
from app.evidence_matcher import match_requirement


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
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_evidence():
    """Load the verified Evidence Library."""
    return load_json(EVIDENCE_FILE)


def load_job_intelligence(job_id: str):
    """Load Job Intelligence for a specific job."""
    return load_json(
        INTELLIGENCE_DIR / f"{job_id}.json"
    )


def load_strategy(job_id: str):
    """Load Application Strategy for a specific job."""
    return load_json(
        STRATEGY_DIR / f"{job_id}.json"
    )


def find_evidence_for_requirement(
    requirement_name: str,
    evidence: list[dict]
):
    """
    Find verified evidence for a job requirement using
    the centralized Evidence Matcher.

    Returns EvidenceMatch objects so Profile Tailor uses
    the same DIRECT / TRANSFERABLE / WEAK / NO_MATCH
    classification as the rest of CareerOS.
    """
    evidence_items = [
        EvidenceItem.model_validate(item)
        for item in evidence
        if item["status"] == "VERIFIED"
    ]

    return match_requirement(
        requirement_name,
        evidence_items,
    )

def build_profile_tailor(job_id: str):
    """
    Build an evidence-grounded profile for one job.

    Every tailored claim must be connected to verified
    evidence.

    No evidence = no claim.
    """

    intelligence = load_job_intelligence(job_id)
    strategy = load_strategy(job_id)
    evidence = load_evidence()

    matched_claims = []
    transferable_claims = []
    missing_requirements = []
    evidence_map = []

    for requirement in intelligence["requirements"]:
        requirement_name = requirement["name"]

        matches = find_evidence_for_requirement(
            requirement_name,
            evidence
        )

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

        # -------------------------------------------------
        # DIRECT VERIFIED EVIDENCE
        # -------------------------------------------------
        if direct_matches:
            selected = direct_matches[0]

            evidence_item = next(
                (
                    item
                    for item in evidence
                    if item["id"] == selected.evidence_id
                ),
                None
            )

            if evidence_item is None:
                missing_requirements.append(
                    requirement_name
                )
                continue

            claim = TailoredClaim(
                requirement=requirement_name,
                suggested_claim=evidence_item["claim"],
                evidence_id=selected.evidence_id,
                evidence_type="DIRECT",
                confidence="HIGH",
                allowed=True,
            )

            matched_claims.append(claim)

            evidence_map.append(
                EvidenceMapping(
                    requirement=requirement_name,
                    evidence_ids=[
                        selected.evidence_id
                    ],
                    match_type="DIRECT",
                    confidence="HIGH",
                    source=[
                        evidence_item["source"]
                    ],
                    suggested_claim=evidence_item["claim"],
                    allowed=True,
                    human_review_required=True,
                )
            )

            continue

        # -------------------------------------------------
        # TRANSFERABLE VERIFIED EVIDENCE
        # -------------------------------------------------
        if transferable_matches:
            selected = transferable_matches[0]

            evidence_item = next(
                (
                    item
                    for item in evidence
                    if item["id"] == selected.evidence_id
                ),
                None
            )

            if evidence_item is None:
                missing_requirements.append(
                    requirement_name
                )
                continue

            claim = TailoredClaim(
                requirement=requirement_name,
                suggested_claim=evidence_item["claim"],
                evidence_id=selected.evidence_id,
                evidence_type="TRANSFERABLE",
                confidence="MEDIUM",
                allowed=True,
            )

            transferable_claims.append(claim)

            evidence_map.append(
                EvidenceMapping(
                    requirement=requirement_name,
                    evidence_ids=[
                        selected.evidence_id
                    ],
                    match_type="TRANSFERABLE",
                    confidence="MEDIUM",
                    source=[
                        evidence_item["source"]
                    ],
                    suggested_claim=evidence_item["claim"],
                    allowed=True,
                    human_review_required=True,
                )
            )

            continue

        # -------------------------------------------------
        # NO USABLE EVIDENCE
        # -------------------------------------------------
        missing_requirements.append(
            requirement_name
        )

        evidence_map.append(
            EvidenceMapping(
                requirement=requirement_name,
                evidence_ids=[],
                match_type="MISSING",
                confidence="UNKNOWN",
                source=[],
                suggested_claim="",
                allowed=False,
                human_review_required=True,
            )
        )

    positioning_statement = (
        "Customer-focused operations leader with experience "
        "in customer communication, business reviews, "
        "customer experience metrics, people leadership, "
        "project management and continuous improvement."
    )

    result = ProfileTailorOutput(
        job_id=job_id,
        company=intelligence["company"],
        title=intelligence["title"],
        positioning_statement=positioning_statement,
        matched_claims=matched_claims,
        transferable_claims=transferable_claims,
        missing_requirements=missing_requirements,
        forbidden_claims=strategy["forbidden_claims"],
        human_review_required=True,
    )

    return result, evidence_map


def main():

    result, evidence_map = build_profile_tailor(
        "JOB-001"
    )

    print()
    print("=" * 80)
    print("CAREEROS PROFILE TAILOR")
    print("=" * 80)

    print()
    print(f"Company: {result.company}")
    print(f"Role: {result.title}")

    print()
    print(
        f"Matched claims: "
        f"{len(result.matched_claims)}"
    )

    print(
        f"Transferable claims: "
        f"{len(result.transferable_claims)}"
    )

    print(
        f"Missing requirements: "
        f"{len(result.missing_requirements)}"
    )

    print(
        f"Evidence mappings: "
        f"{len(evidence_map)}"
    )

    print(
        f"Forbidden claims: "
        f"{len(result.forbidden_claims)}"
    )

    print(
        f"Human review required: "
        f"{result.human_review_required}"
    )

    print()
    print("EVIDENCE MAP")
    print("-" * 80)

    for mapping in evidence_map:

        print(
            f"{mapping.requirement} "
            f"-> {mapping.match_type} "
            f"-> {mapping.evidence_ids}"
        )

        print(
            f"   Confidence: "
            f"{mapping.confidence}"
        )

        print(
            f"   Allowed: "
            f"{mapping.allowed}"
        )

        print(
            f"   Human review: "
            f"{mapping.human_review_required}"
        )

        if mapping.suggested_claim:
            print(
                f"   Claim: "
                f"{mapping.suggested_claim}"
            )

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
