from app.models.supervisor_case import AgentFinding
from app.models.candidate_finding import CandidateFinding


def build_risk_finding(
    opportunity: dict,
    decision: dict,
    candidate_finding: CandidateFinding | None = None,
) -> AgentFinding:
    risks = []
    evidence_refs = []

    critical_gaps = opportunity.get(
        "critical_gaps",
        [],
    )

    core_gaps = opportunity.get(
        "core_gaps",
        [],
    )

    if critical_gaps:
        risks.extend(
            [
                f"Critical evidence gap: {gap}"
                for gap in critical_gaps
            ]
        )

    if core_gaps:
        risks.extend(
            [
                f"Core capability gap: {gap}"
                for gap in core_gaps
            ]
        )

    forbidden_claims = decision.get(
        "forbidden_claims",
        [],
    )

    if candidate_finding is not None:
        transition_gaps = [
            gap
            for gap in candidate_finding.explicit_gaps
            if gap in {
                "Formal SaaS experience",
                "CRM expertise",
                "Enterprise account ownership",
            }
        ]

        other_gaps = [
            gap
            for gap in candidate_finding.explicit_gaps
            if gap not in transition_gaps
        ]

        if other_gaps:
            risks.extend(
                [
                    f"Candidate finding identifies an explicit gap: {gap}"
                    for gap in other_gaps
                ]
            )

        if transition_gaps:
            risks.append(
                "Non-blocking transition risk: "
                "strong transferable Customer Success capability is present, "
                "but the following formal experience is not verified: "
                + ", ".join(transition_gaps)
                + "."
            )

        if candidate_finding.forbidden_assumptions:
            evidence_refs.extend(
                candidate_finding.verified_evidence_refs
            )

    if forbidden_claims:
        risks.append(
            "Some candidate capabilities are explicitly "
            "not safe to claim without supporting evidence."
        )

    # These are known career-transition risks already represented
    # in the candidate truth system.
    if not risks:
        risks.append(
            "No critical evidence risk identified, "
            "but formal SaaS/CRM/account-ownership experience "
            "should not be assumed."
        )

    blocking_risk = bool(
        critical_gaps
        or core_gaps
        or forbidden_claims
        or other_gaps
    )

    recommendation = (
        "REVIEW"
        if blocking_risk
        else "APPLY"
    )

    confidence = (
        0.95
        if critical_gaps
        else 0.85
        if candidate_finding is not None
        else 0.80
    )

    return AgentFinding(
        agent="Risk Agent",
        finding=(
            " ".join(risks)
        ),
        confidence=confidence,
        evidence_refs=evidence_refs,
        risks=risks,
        recommendation=recommendation,
    )
