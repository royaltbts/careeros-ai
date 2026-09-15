import json
from pathlib import Path

from app.models.evidence import EvidenceItem


EVIDENCE_PATH = Path("data/evidence/evidence.json")


def load_verified_evidence() -> list[EvidenceItem]:
    with open(EVIDENCE_PATH, "r") as f:
        raw = json.load(f)

    evidence = [
        EvidenceItem.model_validate(item)
        for item in raw
    ]

    return [
        item
        for item in evidence
        if item.status == "VERIFIED"
    ]


def select_outreach_evidence(
    capabilities: list[str],
    max_items: int = 3,
) -> list[EvidenceItem]:
    """
    Select verified evidence relevant to the supplied
    Customer Success capabilities.

    No unverified evidence is returned.
    """

    evidence = load_verified_evidence()

    selected = []

    capability_map = {
        "customer communication": "CUSTOMER_COMMUNICATION",
        "stakeholder management": "CUSTOMER_COMMUNICATION",
        "business reviews": "CUSTOMER_COMMUNICATION",
        "customer satisfaction": "CUSTOMER_SATISFACTION",
        "customer experience": "CUSTOMER_SATISFACTION",
        "service performance": "CUSTOMER_SATISFACTION",
        "continuous improvement": "CONTINUOUS_IMPROVEMENT",
        "process optimization": "CONTINUOUS_IMPROVEMENT",
        "customer experience improvement": "CONTINUOUS_IMPROVEMENT",
        "customer problem solving": "CUSTOMER_PROBLEM_SOLVING",
        "people leadership": "PEOPLE_LEADERSHIP",
        "project management": "PROJECT_MANAGEMENT",
    }

    normalized_capabilities = {
        capability.strip().lower()
        for capability in capabilities
    }

    target_capabilities = {
        capability_map[capability]
        for capability in normalized_capabilities
        if capability in capability_map
    }

    for item in evidence:
        if item.capability in target_capabilities:
            selected.append(item)

        if len(selected) >= max_items:
            break

    return selected
