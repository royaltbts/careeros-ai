from app.models.supervisor_case import (
    AgentFinding,
    SupervisorCase,
)

from app.risk_agent import build_risk_finding


def build_supervisor_case(
    opportunity: dict,
    decision: dict,
    safety: dict | None = None,
) -> SupervisorCase:
    """
    Build a shared Supervisor Case from existing
    CareerOS intelligence outputs.

    This function does not change any existing decision.
    """

    findings = []
    disagreements = []
    unresolved_questions = []

    # --------------------------------------------------
    # Candidate Fit
    # --------------------------------------------------

    fit_score = opportunity.get(
        "fit_score",
        0.0,
    )

    fit_confidence = min(
        max(fit_score / 100.0, 0.0),
        1.0,
    )

    findings.append(
        AgentFinding(
            agent="Candidate Fit Agent",
            finding=(
                f"Candidate fit score: {fit_score:.2f}."
            ),
            confidence=fit_confidence,
            evidence_refs=[
                item["requirement"]
                for item in opportunity.get(
                    "requirement_analysis",
                    []
                )
            ],
            recommendation=(
                "APPLY"
                if fit_score >= 80
                else "REVIEW"
            ),
        )
    )

    # --------------------------------------------------
    # Company Strategic Fit
    # --------------------------------------------------

    strategic_fit = (
        opportunity.get(
            "company_strategic_fit"
        )
        or {}
    )

    strategic_alignment = strategic_fit.get(
        "strategic_alignment"
    )

    research_quality = strategic_fit.get(
        "research_quality"
    )

    if strategic_alignment is not None:
        findings.append(
            AgentFinding(
                agent="Company Intelligence Agent",
                finding=(
                    "Company strategic alignment: "
                    f"{strategic_alignment:.2f}."
                ),
                confidence=min(
                    max(
                        strategic_alignment / 100.0,
                        0.0,
                    ),
                    1.0,
                ),
                evidence_refs=[
                    "strategic_alignment"
                ],
                recommendation=(
                    "APPLY"
                    if strategic_alignment >= 75
                    else "REVIEW"
                ),
            )
        )

    # --------------------------------------------------
    # Research Quality
    # --------------------------------------------------

    if research_quality is not None:
        findings.append(
            AgentFinding(
                agent="Research Quality Agent",
                finding=(
                    "Company research quality: "
                    f"{research_quality:.2f}."
                ),
                confidence=min(
                    max(
                        research_quality / 100.0,
                        0.0,
                    ),
                    1.0,
                ),
                evidence_refs=[
                    "research_quality"
                ],
                risks=(
                    [
                        "Company research is limited."
                    ]
                    if research_quality < 75
                    else []
                ),
                recommendation=(
                    "APPLY"
                    if research_quality >= 75
                    else "REVIEW"
                ),
            )
        )

    # --------------------------------------------------
    # Opportunity Decision
    # --------------------------------------------------

    opportunity_recommendation = decision.get(
        "recommendation",
        "REVIEW",
    )

    opportunity_score = opportunity.get(
        "opportunity_score",
        0.0,
    )

    findings.append(
        AgentFinding(
            agent="Opportunity Decision Agent",
            finding=(
                f"Opportunity score: {opportunity_score:.2f}; "
                f"recommendation: "
                f"{opportunity_recommendation}."
            ),
            confidence=min(
                max(
                    opportunity_score / 100.0,
                    0.0,
                ),
                1.0,
            ),
            evidence_refs=[
                "opportunity_score",
                "priority",
                "recommendation",
            ],
            recommendation=opportunity_recommendation,
        )
    )

    # --------------------------------------------------
    # Risk
    # --------------------------------------------------

    risk_finding = build_risk_finding(
        opportunity,
        decision,
    )

    findings.append(
        risk_finding
    )

    # --------------------------------------------------
    # Safety
    # --------------------------------------------------

    if safety is not None:
        safe = safety.get(
            "all_claims_safe",
            False,
        )

        findings.append(
            AgentFinding(
                agent="Claim Safety Agent",
                finding=(
                    "All claims passed safety governance."
                    if safe
                    else "One or more claims failed safety governance."
                ),
                confidence=1.0 if safe else 0.0,
                evidence_refs=[
                    "claim_safety"
                ],
                risks=(
                    []
                    if safe
                    else [
                        "Unsafe claim detected."
                    ]
                ),
                recommendation=(
                    "APPLY"
                    if safe
                    else "REVIEW"
                ),
            )
        )

    # --------------------------------------------------
    # Detect disagreements
    # --------------------------------------------------

    recommendations = {
        finding.agent: finding.recommendation
        for finding in findings
        if finding.recommendation
    }

    recommendation_values = set(
        recommendations.values()
    )

    if len(recommendation_values) > 1:
        risk_finding = next(
            (
                finding
                for finding in findings
                if finding.agent == "Risk Agent"
            ),
            None,
        )

        disagreement_topic = (
            "Formal SaaS/CRM/account-ownership experience"
            if risk_finding
            and any(
                term in risk.lower()
                for risk in risk_finding.risks
                for term in [
                    "saas",
                    "crm",
                    "account-ownership",
                    "account ownership",
                ]
            )
            else (
                risk_finding.risks[0]
                if risk_finding
                and risk_finding.risks
                else "Overall recommendation"
            )
        )

        disagreements.append(
            {
                "agents": list(
                    recommendations.keys()
                ),
                "topic": disagreement_topic,
                "positions": [
                    f"{agent}: {recommendation}"
                    for agent, recommendation
                    in recommendations.items()
                ],
                "resolution_required": True,
            }
        )

    # Convert raw disagreement dictionaries through Pydantic
    from app.models.supervisor_case import (
        AgentDisagreement,
    )

    typed_disagreements = [
        AgentDisagreement.model_validate(
            disagreement
        )
        for disagreement in disagreements
    ]

    if research_quality is not None and research_quality < 75:
        unresolved_questions.append(
            "Is additional company research required "
            "before significant application effort?"
        )

    return SupervisorCase(
        job_id=opportunity["job_id"],
        company=opportunity["company"],
        title=opportunity["title"],
        findings=findings,
        disagreements=typed_disagreements,
        unresolved_questions=unresolved_questions,
        human_review_required=True,
    )
