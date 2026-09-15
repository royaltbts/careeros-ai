from app.models.supervisor_case import AgentFinding


def build_risk_finding(
    opportunity: dict,
    decision: dict,
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

    recommendation = (
        "REVIEW"
        if risks
        else "APPLY"
    )

    confidence = (
        0.95
        if critical_gaps
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
