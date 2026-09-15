from app.evidence_retriever import retrieve_evidence
from app.models.evidence import EvidenceItem
from app.models.evidence_match import EvidenceMatch


from app.capability_map import CAPABILITY_RELATIONSHIPS


def classify_evidence_match(
    requirement: str,
    evidence: EvidenceItem,
    score: float,
) -> EvidenceMatch:

    requirement_text = requirement.lower()
    allowed_use = {
        value.lower()
        for value in evidence.allowed_use
    }

    capability = evidence.capability.strip().lower().replace("_", " ")

    # Explicit evidence in the requirement.
    if (
        "business review" in requirement_text
        and "business reviews" in allowed_use
    ):
        return EvidenceMatch(
            requirement=requirement,
            evidence_id=evidence.id,
            match_type="DIRECT",
            score=score,
            rationale=(
                "The evidence explicitly documents "
                "business review experience."
            ),
            suggested_use="Verified application evidence",
        )

    if (
        "continuous improvement" in requirement_text
        and "continuous improvement" in allowed_use
    ):
        return EvidenceMatch(
            requirement=requirement,
            evidence_id=evidence.id,
            match_type="DIRECT",
            score=score,
            rationale=(
                "The evidence explicitly documents "
                "continuous improvement experience."
            ),
            suggested_use="Verified application evidence",
        )

    if (
        "customer experience" in requirement_text
        and "customer experience" in allowed_use
    ):
        return EvidenceMatch(
            requirement=requirement,
            evidence_id=evidence.id,
            match_type="DIRECT",
            score=score,
            rationale=(
                "The Evidence Library explicitly "
                "allows this evidence for customer "
                "experience use."
            ),
            suggested_use="Verified application evidence",
        )

    # Capability-level relationship.
    related_capabilities = (
        CAPABILITY_RELATIONSHIPS.get(
            capability,
            set(),
        )
    )

    normalized_requirement = (
        requirement_text.replace("-", " ")
    )

    if any(
        related.replace("_", " ").lower()
        in normalized_requirement
        for related in related_capabilities
    ):
        return EvidenceMatch(
            requirement=requirement,
            evidence_id=evidence.id,
            match_type="TRANSFERABLE",
            score=score,
            rationale=(
                "The evidence supports a related "
                "capability but does not directly "
                "prove the requirement."
            ),
            suggested_use="Human-reviewed transferable evidence",
        )

    if score >= 0.20:
        return EvidenceMatch(
            requirement=requirement,
            evidence_id=evidence.id,
            match_type="WEAK",
            score=score,
            rationale=(
                "Some textual overlap exists, but "
                "the evidence does not establish "
                "the requested capability."
            ),
            suggested_use=None,
        )

    return EvidenceMatch(
        requirement=requirement,
        evidence_id=evidence.id,
        match_type="NO_MATCH",
        score=score,
        rationale=(
            "The evidence does not provide "
            "sufficient support for the requirement."
        ),
        suggested_use=None,
    )


def match_requirement(
    requirement: str,
    evidence_library: list[EvidenceItem],
    top_k: int = 5,
) -> list[EvidenceMatch]:

    retrieved = retrieve_evidence(
        requirement,
        evidence_library,
        top_k=top_k,
    )

    return [
        classify_evidence_match(
            requirement,
            evidence,
            score,
        )
        for evidence, score in retrieved
    ]
