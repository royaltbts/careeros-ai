import re
from pathlib import Path

from app.models.claim_fidelity import ClaimFidelityCheck


BASE_DIR = Path(__file__).resolve().parent.parent

EVIDENCE_FILE = (
    BASE_DIR / "data" / "evidence" / "evidence.json"
)


def load_evidence():
    """Load the Evidence Library."""

    import json

    with open(
        EVIDENCE_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def normalize(text: str) -> str:
    """Normalize text for comparison."""

    return re.sub(
        r"[^a-z0-9%]+",
        " ",
        text.lower()
    ).strip()


def extract_numbers(text: str):
    """Extract numbers and percentages."""

    return re.findall(
        r"\b\d+(?:\.\d+)?%?\b",
        text
    )


def extract_entities(text: str):
    """
    Detect important company/entity terms that should
    be explicitly supported by evidence.
    """

    known_entities = [
        "google",
        "johnson & johnson",
        "saaS",
        "enterprise",
        "crm",
        "snowflake",
        "power bi",
        "jira",
        "confluence",
    ]

    text_lower = text.lower()

    return [
        entity
        for entity in known_entities
        if entity.lower() in text_lower
    ]


def extract_ownership_claims(text: str):
    """
    Detect language that can imply ownership or
    responsibility beyond the evidence.
    """

    ownership_terms = [
        "owned",
        "managed accounts",
        "managed enterprise accounts",
        "account ownership",
        "portfolio",
        "book of business",
        "renewals",
        "renewal ownership",
        "customer retention",
        "retention",
    ]

    text_lower = text.lower()

    return [
        term
        for term in ownership_terms
        if term in text_lower
    ]


def extract_outcome_claims(text: str):
    """
    Detect quantified or strong outcome language.
    """

    outcome_patterns = [
        r"\bincreased\b",
        r"\bimproved\b",
        r"\breduced\b",
        r"\bgenerated\b",
        r"\bachieved\b",
        r"\bsaved\b",
        r"\bgrowth\b",
        r"\bretention\b",
        r"\b\d+(?:\.\d+)?%\b",
    ]

    matches = []

    text_lower = text.lower()

    for pattern in outcome_patterns:

        found = re.findall(
            pattern,
            text_lower
        )

        matches.extend(found)

    return sorted(set(matches))


def build_evidence_text(item: dict) -> str:
    """Combine the evidence fields used for fidelity."""

    return " ".join(
        [
            item.get("claim", ""),
            item.get("evidence", ""),
            " ".join(item.get("allowed_use", [])),
        ]
    )


def check_claim_fidelity(
    claim: str,
    evidence_ids: list[str]
):
    """
    Check whether a claim stays within the boundaries
    of the supplied verified evidence.

    This is a conservative deterministic check.
    Passing this check does NOT replace human review.
    """

    evidence = load_evidence()

    evidence_index = {
        item["id"]: item
        for item in evidence
    }

    evidence_items = []

    for evidence_id in evidence_ids:

        item = evidence_index.get(
            evidence_id
        )

        if item is None:

            return ClaimFidelityCheck(
                claim=claim,
                evidence_ids=evidence_ids,
                supported_terms=[],
                unsupported_terms=[],
                unsupported_numbers=[],
                unsupported_entities=[],
                unsupported_ownership=[],
                supported=False,
                reason=(
                    f"Evidence ID {evidence_id} "
                    "does not exist."
                ),
                human_review_required=True,
            )

        if item["status"] != "VERIFIED":

            return ClaimFidelityCheck(
                claim=claim,
                evidence_ids=evidence_ids,
                supported_terms=[],
                unsupported_terms=[],
                unsupported_numbers=[],
                unsupported_entities=[],
                unsupported_ownership=[],
                supported=False,
                reason=(
                    f"Evidence ID {evidence_id} "
                    "is not verified."
                ),
                human_review_required=True,
            )

        evidence_items.append(item)

    evidence_text = " ".join(
        build_evidence_text(item)
        for item in evidence_items
    )

    normalized_claim = normalize(claim)
    normalized_evidence = normalize(
        evidence_text
    )

    claim_words = set(
        normalized_claim.split()
    )

    evidence_words = set(
        normalized_evidence.split()
    )

    supported_terms = sorted(
        claim_words.intersection(
            evidence_words
        )
    )

    unsupported_terms = sorted(
        claim_words.difference(
            evidence_words
        )
    )

    # ---------------------------------------------
    # Numbers
    # ---------------------------------------------

    claim_numbers = extract_numbers(
        claim
    )

    evidence_numbers = extract_numbers(
        evidence_text
    )

    unsupported_numbers = [
        number
        for number in claim_numbers
        if number not in evidence_numbers
    ]

    # ---------------------------------------------
    # Entities
    # ---------------------------------------------

    claim_entities = extract_entities(
        claim
    )

    evidence_entities = extract_entities(
        evidence_text
    )

    unsupported_entities = [
        entity
        for entity in claim_entities
        if entity not in evidence_entities
    ]

    # ---------------------------------------------
    # Ownership
    # ---------------------------------------------

    claim_ownership = extract_ownership_claims(
        claim
    )

    evidence_ownership = extract_ownership_claims(
        evidence_text
    )

    unsupported_ownership = [
        term
        for term in claim_ownership
        if term not in evidence_ownership
    ]

    # ---------------------------------------------
    # Strong outcome claims
    # ---------------------------------------------

    outcome_claims = extract_outcome_claims(
        claim
    )

    evidence_outcomes = extract_outcome_claims(
        evidence_text
    )

    unsupported_outcomes = [
        term
        for term in outcome_claims
        if term not in evidence_outcomes
    ]

    # ---------------------------------------------
    # Determine support
    # ---------------------------------------------

    reasons = []

    if unsupported_numbers:

        reasons.append(
            "Unsupported numbers: "
            + ", ".join(
                unsupported_numbers
            )
        )

    if unsupported_entities:

        reasons.append(
            "Unsupported entities: "
            + ", ".join(
                unsupported_entities
            )
        )

    if unsupported_ownership:

        reasons.append(
            "Unsupported ownership language: "
            + ", ".join(
                unsupported_ownership
            )
        )

    if unsupported_outcomes:

        reasons.append(
            "Unsupported outcome language: "
            + ", ".join(
                unsupported_outcomes
            )
        )

    supported = not reasons

    if supported:

        reason = (
            "Claim stays within the detectable "
            "boundaries of the supplied evidence."
        )

    else:

        reason = "; ".join(
            reasons
        )

    return ClaimFidelityCheck(
        claim=claim,
        evidence_ids=evidence_ids,
        supported_terms=supported_terms,
        unsupported_terms=unsupported_terms,
        unsupported_numbers=unsupported_numbers,
        unsupported_entities=unsupported_entities,
        unsupported_ownership=unsupported_ownership,
        supported=supported,
        reason=reason,
        human_review_required=True,
    )


def main():

    print()
    print("=" * 80)
    print("CAREEROS CLAIM FIDELITY CHECK")
    print("=" * 80)

    # ---------------------------------------------
    # TEST 1: Legitimate claim
    # ---------------------------------------------

    legitimate_claim = (
        "Managed customer experience performance "
        "through CSAT, SLA, WFM and RCR metrics."
    )

    result_1 = check_claim_fidelity(
        legitimate_claim,
        ["EV003"]
    )

    print()
    print("TEST 1: LEGITIMATE CLAIM")
    print("-" * 80)
    print(
        f"Supported: "
        f"{result_1.supported}"
    )
    print(
        f"Reason: "
        f"{result_1.reason}"
    )

    # ---------------------------------------------
    # TEST 2: Obviously fabricated claim
    # ---------------------------------------------

    fabricated_claim = (
        "Managed 50 enterprise SaaS accounts "
        "and increased retention by 35%."
    )

    result_2 = check_claim_fidelity(
        fabricated_claim,
        ["EV003"]
    )

    print()
    print("TEST 2: UNSUPPORTED CLAIM")
    print("-" * 80)
    print(
        f"Supported: "
        f"{result_2.supported}"
    )
    print(
        f"Reason: "
        f"{result_2.reason}"
    )

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
