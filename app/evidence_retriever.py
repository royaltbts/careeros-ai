import re
from typing import List, Tuple

from app.models.evidence import EvidenceItem
from app.capability_map import CAPABILITY_RELATIONSHIPS


STOP_WORDS = {
    "a",
    "an",
    "and",
    "the",
    "to",
    "of",
    "in",
    "for",
    "with",
    "on",
    "as",
    "is",
    "are",
    "be",
    "or",
    "by",
    "from",
    "this",
    "that",
}


def _tokens(text: str) -> set[str]:
    words = re.findall(
        r"[a-zA-Z0-9]+",
        text.lower(),
    )

    return {
        word
        for word in words
        if word not in STOP_WORDS
    }


def _evidence_text(
    item: EvidenceItem,
) -> str:

    return " ".join(
        [
            item.capability,
            item.claim,
            item.evidence,
            " ".join(item.allowed_use),
        ]
    )


def _capability_terms(
    requirement: str,
) -> set[str]:

    requirement_lower = requirement.lower()

    terms = set()

    for capability, related in (
        CAPABILITY_RELATIONSHIPS.items()
    ):
        capability_phrase = (
            capability.lower()
        )

        if capability_phrase in requirement_lower:
            terms.add(capability_phrase)

        for related_capability in related:
            related_phrase = (
                related_capability.lower()
            )

            if related_phrase in requirement_lower:
                terms.add(related_phrase)

    return terms


def _capability_score(
    requirement: str,
    evidence: EvidenceItem,
) -> float:

    requirement_lower = requirement.lower()

    evidence_capability = (
        evidence.capability.lower()
    )

    evidence_allowed_use = {
        value.lower()
        for value in evidence.allowed_use
    }

    matched_terms = _capability_terms(
        requirement
    )

    if not matched_terms:
        return 0.0

    if evidence_capability in matched_terms:
        return 1.0

    if any(
        term in evidence_allowed_use
        for term in matched_terms
    ):
        return 0.8

    related_capabilities = (
        CAPABILITY_RELATIONSHIPS.get(
            evidence_capability,
            [],
        )
    )

    if any(
        related.lower() in matched_terms
        for related in related_capabilities
    ):
        return 0.5

    return 0.0


def _score_requirement(
    requirement: str,
    evidence: EvidenceItem,
) -> float:

    requirement_tokens = _tokens(
        requirement
    )

    evidence_tokens = _tokens(
        _evidence_text(evidence)
    )

    if not requirement_tokens:
        lexical_score = 0.0
    else:
        overlap = (
            requirement_tokens
            & evidence_tokens
        )

        lexical_score = (
            len(overlap)
            / len(requirement_tokens)
        )

    capability_score = _capability_score(
        requirement,
        evidence,
    )

    return max(
        lexical_score,
        capability_score,
    )


def retrieve_evidence(
    requirement: str,
    evidence_library: List[EvidenceItem],
    top_k: int = 5,
) -> List[Tuple[EvidenceItem, float]]:

    candidates = []

    for evidence in evidence_library:

        if evidence.status != "VERIFIED":
            continue

        score = _score_requirement(
            requirement,
            evidence,
        )

        if score > 0:
            candidates.append(
                (evidence, score)
            )

    candidates.sort(
        key=lambda item: item[1],
        reverse=True,
    )

    return candidates[:top_k]
