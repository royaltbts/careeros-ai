from app.models.career_strategy import CareerStrategy
from app.models.company_intelligence import CompanyIntelligence
from app.capability_map import CAPABILITY_RELATIONSHIPS

from app.company_research_quality import (
    calculate_research_quality,
)


VALID_RESEARCH_STATUSES = {
    "WEB_RESEARCHED",
    "ROLE_DERIVED",
    "MOCK",
}


def calculate_company_strategic_fit(
    intelligence: CompanyIntelligence,
    strategy: CareerStrategy,
) -> dict:
    """
    Calculate how strategically aligned a company context is
    with the candidate's Customer Success career strategy.

    This is separate from Candidate Fit.

    Candidate Fit asks:
        Can the candidate credibly perform the role?

    Company Strategic Fit asks:
        Does the company/context align with the candidate's
        strategic Customer Success direction?

    No candidate claims are created here.
    """

    research_status = intelligence.research_status

    if research_status not in VALID_RESEARCH_STATUSES:
        raise ValueError(
            f"Unsupported research status: {research_status}"
        )

    priority_capabilities = {
        capability.strip().lower()
        for capability in strategy.priority_capabilities
    }

    direct_matches = []
    related_matches = []

    for priority in intelligence.likely_cs_priorities:
        priority_normalized = priority.strip().lower()

        if priority_normalized in priority_capabilities:
            direct_matches.append(priority)
            continue

        related = CAPABILITY_RELATIONSHIPS.get(
            priority_normalized,
            [],
        )

        if any(
            capability.lower() in priority_capabilities
            for capability in related
        ):
            related_matches.append(priority)

    total_priorities = len(
        intelligence.likely_cs_priorities
    )

    if total_priorities == 0:
        base_score = 0.0
    else:
        weighted_matches = (
            len(direct_matches)
            + (len(related_matches) * 0.5)
        )

        base_score = (
            weighted_matches / total_priorities
        ) * 100.0

    # Keep strategic alignment separate from research confidence.
    strategic_alignment = max(
        min(base_score, 100.0),
        0.0,
    )

    research_coverage = None
    research_evidence_confidence = None
    research_quality_score = None

    if research_status == "WEB_RESEARCHED":
        research_quality = calculate_research_quality(
            intelligence
        )

        research_coverage = research_quality[
            "coverage"
        ]

        research_evidence_confidence = (
            research_quality["confidence"]
        )

        research_quality_score = (
            research_quality["score"]
        )

        # Backward-compatible field used by the
        # existing Opportunity Decision layer.
        research_confidence = research_quality_score

    else:
        research_confidence = {
            "ROLE_DERIVED": 75.0,
            "MOCK": 0.0,
        }[research_status]

    risk_penalty = min(
        len(intelligence.potential_risks) * 10.0,
        30.0,
    )

    # Decision-ready fit combines alignment, research confidence,
    # and known company risks. The underlying strategic alignment
    # remains visible and is never reduced by research confidence.
    decision_ready_fit = (
        strategic_alignment
        * (research_confidence / 100.0)
    )

    decision_ready_fit = max(
        min(decision_ready_fit - risk_penalty, 100.0),
        0.0,
    )

    if strategic_alignment >= 75:
        assessment = "STRONG"
    elif strategic_alignment >= 50:
        assessment = "MODERATE"
    elif strategic_alignment > 0:
        assessment = "WEAK"
    else:
        assessment = "UNKNOWN"

    if research_status == "MOCK":
        assessment = "TEST_ONLY"

    if total_priorities == 0:
        reason = (
            "No Customer Success priorities were available "
            "for strategic alignment assessment."
        )
    elif direct_matches or related_matches:
        reason = (
            f"Matched {len(direct_matches)} direct and "
            f"{len(related_matches)} related Customer Success "
            f"priority capabilities. Research status: "
            f"{research_status}."
        )
    else:
        reason = (
            "No Customer Success priorities matched the "
            "candidate's strategic capabilities."
        )

    return {
        "company": intelligence.company,
        "score": round(decision_ready_fit, 2),
        "strategic_alignment": round(strategic_alignment, 2),
        "research_confidence": round(research_confidence, 2),
        "research_coverage": (
            round(research_coverage, 2)
            if research_coverage is not None
            else None
        ),
        "research_evidence_confidence": (
            round(research_evidence_confidence, 2)
            if research_evidence_confidence is not None
            else None
        ),
        "research_quality": (
            round(research_quality_score, 2)
            if research_quality_score is not None
            else None
        ),
        "decision_ready_fit": round(decision_ready_fit, 2),
        "assessment": assessment,
        "research_status": research_status,
        "direct_matches": direct_matches,
        "related_matches": related_matches,
        "risk_penalty": round(risk_penalty, 2),
        "reason": reason,
        "human_review_required": True,
    }
