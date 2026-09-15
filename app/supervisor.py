from app.models.supervisor_decision import (
    SupervisorDecision,
    SupervisorFinding,
)


def build_supervisor_decision(
    opportunity: dict,
    decision: dict,
    safety: dict | None = None,
) -> SupervisorDecision:
    """
    Reconcile existing CareerOS signals into a
    higher-level supervisory recommendation.

    This layer does not recalculate candidate fit
    or opportunity scoring.
    """

    findings = []
    conflicts = []
    unresolved_questions = []

    opportunity_score = opportunity.get(
        "opportunity_score",
        0.0,
    )

    fit_score = opportunity.get(
        "fit_score",
        0.0,
    )

    priority = opportunity.get(
        "priority",
        "LOW",
    )

    recommendation = decision.get(
        "recommendation",
        "REVIEW",
    )

    strategic_fit = (
        opportunity.get("company_strategic_fit")
        or {}
    )

    strategic_alignment = strategic_fit.get(
        "strategic_alignment"
    )

    research_quality = strategic_fit.get(
        "research_quality"
    )

    critical_gaps = opportunity.get(
        "critical_gaps",
        [],
    )

    # --------------------------------------------------
    # Candidate fit finding
    # --------------------------------------------------

    fit_confidence = min(
        max(fit_score / 100.0, 0.0),
        1.0,
    )

    findings.append(
        SupervisorFinding(
            source="Candidate Fit",
            finding=(
                f"Candidate fit score is {fit_score:.2f}."
            ),
            confidence=fit_confidence,
            evidence_refs=(
                opportunity.get(
                    "requirement_analysis",
                    []
                )
                and [
                    item["requirement"]
                    for item in opportunity[
                        "requirement_analysis"
                    ]
                ]
                or []
            ),
        )
    )

    # --------------------------------------------------
    # Opportunity finding
    # --------------------------------------------------

    opportunity_confidence = min(
        max(opportunity_score / 100.0, 0.0),
        1.0,
    )

    findings.append(
        SupervisorFinding(
            source="Opportunity Decision",
            finding=(
                f"Opportunity is {priority} priority "
                f"with score {opportunity_score:.2f} "
                f"and recommendation {recommendation}."
            ),
            confidence=opportunity_confidence,
            evidence_refs=[
                "opportunity_score",
                "priority",
                "recommendation",
            ],
        )
    )

    # --------------------------------------------------
    # Company strategic fit
    # --------------------------------------------------

    if strategic_alignment is not None:
        findings.append(
            SupervisorFinding(
                source="Company Strategic Fit",
                finding=(
                    f"Company strategic alignment is "
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
            )
        )

    if research_quality is not None:
        findings.append(
            SupervisorFinding(
                source="Research Quality",
                finding=(
                    f"Company research quality is "
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
            )
        )

    # --------------------------------------------------
    # Safety finding
    # --------------------------------------------------

    if safety is not None:
        all_claims_safe = safety.get(
            "all_claims_safe",
            False,
        )

        findings.append(
            SupervisorFinding(
                source="Claim Safety",
                finding=(
                    "All claims passed safety governance."
                    if all_claims_safe
                    else "One or more claims failed safety governance."
                ),
                confidence=1.0 if all_claims_safe else 0.0,
                evidence_refs=[
                    "claim_safety"
                ],
            )
        )

    # --------------------------------------------------
    # Conflict detection
    # --------------------------------------------------

    if critical_gaps:
        conflicts.append(
            "Opportunity is attractive but contains "
            "critical evidence gaps."
        )

    if (
        recommendation == "APPLY"
        and research_quality is not None
        and research_quality < 75
    ):
        conflicts.append(
            "Application recommendation is strong, "
            "but company research quality is limited."
        )

    if (
        strategic_alignment is not None
        and strategic_alignment < 50
        and priority == "HIGH"
    ):
        conflicts.append(
            "Opportunity priority is HIGH despite "
            "weak company strategic alignment."
        )

    # --------------------------------------------------
    # Unresolved questions
    # --------------------------------------------------

    if research_quality is not None and research_quality < 75:
        unresolved_questions.append(
            "Is additional company research needed "
            "before significant application effort?"
        )

    if critical_gaps:
        unresolved_questions.append(
            "Can the identified critical gaps be "
            "credibly addressed through transferable experience?"
        )

    # --------------------------------------------------
    # Supervisory recommendation
    # --------------------------------------------------

    if priority == "LOW":
        supervisor_recommendation = "SKIP"

    elif critical_gaps:
        supervisor_recommendation = "REVIEW"

    elif safety is not None and not safety.get(
        "all_claims_safe",
        False,
    ):
        supervisor_recommendation = "REVIEW"

    elif conflicts:
        supervisor_recommendation = "REVIEW"

    elif recommendation == "APPLY":
        supervisor_recommendation = "APPLY"

    elif recommendation == "SKIP":
        supervisor_recommendation = "SKIP"

    else:
        supervisor_recommendation = "REVIEW"

    # --------------------------------------------------
    # Confidence
    # --------------------------------------------------

    confidence_components = [
        fit_confidence,
        opportunity_confidence,
    ]

    if strategic_alignment is not None:
        confidence_components.append(
            strategic_alignment / 100.0
        )

    if research_quality is not None:
        confidence_components.append(
            research_quality / 100.0
        )

    if safety is not None:
        confidence_components.append(
            1.0
            if safety.get(
                "all_claims_safe",
                False,
            )
            else 0.0
        )

    confidence = (
        sum(confidence_components)
        / len(confidence_components)
    )

    if conflicts:
        confidence *= 0.85

    if unresolved_questions:
        confidence *= 0.95

    confidence = round(
        min(max(confidence, 0.0), 1.0),
        4,
    )

    return SupervisorDecision(
        job_id=opportunity["job_id"],
        company=opportunity["company"],
        title=opportunity["title"],
        recommendation=supervisor_recommendation,
        confidence=confidence,
        findings=findings,
        conflicts=conflicts,
        unresolved_questions=unresolved_questions,
        human_review_required=True,
        external_action_allowed=False,
    )


def build_supervisor_decision_from_case(
    case,
    base_decision: dict,
) -> SupervisorDecision:
    """
    Resolve a SupervisorCase produced by specialist agents.

    The Supervisor evaluates the type and severity of
    disagreements instead of treating every disagreement
    as an automatic blocker.
    """

    findings = [
        SupervisorFinding(
            source=finding.agent,
            finding=finding.finding,
            confidence=finding.confidence,
            evidence_refs=finding.evidence_refs,
        )
        for finding in case.findings
    ]

    conflicts = []
    unresolved_questions = list(
        case.unresolved_questions
    )

    recommendation = base_decision.get(
        "recommendation",
        "REVIEW",
    )

    # --------------------------------------------------
    # Classify disagreements
    # --------------------------------------------------

    hard_blockers = []
    caution_disagreements = []

    for disagreement in case.disagreements:
        positions = [
            position.upper()
            for position in disagreement.positions
        ]

        has_review = any(
            "REVIEW" in position
            for position in positions
        )

        has_apply = any(
            "APPLY" in position
            for position in positions
        )

        if has_review and has_apply:
            related_risk_finding = next(
                (
                    finding
                    for finding in findings
                    if finding.source == "Risk Agent"
                ),
                None,
            )

            risk_text = (
                related_risk_finding.finding.lower()
                if related_risk_finding
                else ""
            )

            critical_terms = (
                "critical evidence gap",
                "unsafe",
                "fabricat",
                "forbidden",
                "missing required evidence",
            )

            if any(
                term in risk_text
                for term in critical_terms
            ):
                hard_blockers.append(
                    disagreement.topic
                )
            else:
                caution_disagreements.append(
                    disagreement.topic
                )

    # --------------------------------------------------
    # Hard blockers
    # --------------------------------------------------

    if hard_blockers:
        conflicts.extend(
            [
                f"Supervisor identified a blocking disagreement: "
                f"{topic}."
                for topic in hard_blockers
            ]
        )

    # --------------------------------------------------
    # Caution disagreements
    # --------------------------------------------------

    if caution_disagreements:
        conflicts.extend(
            [
                f"Supervisor identified a non-blocking risk "
                f"requiring human review: {topic}."
                for topic in caution_disagreements
            ]
        )

        unresolved_questions.append(
            "Human reviewer should assess whether the identified "
            "transferable experience risk materially affects the opportunity."
        )

    # --------------------------------------------------
    # Resolve recommendation
    # --------------------------------------------------

    if hard_blockers:
        supervisor_recommendation = "REVIEW"
    elif recommendation == "SKIP":
        supervisor_recommendation = "SKIP"
    elif recommendation == "APPLY":
        supervisor_recommendation = "APPLY"
    else:
        supervisor_recommendation = "REVIEW"

    # --------------------------------------------------
    # Supervisor resolution explanation
    # --------------------------------------------------

    if hard_blockers:
        findings.append(
            SupervisorFinding(
                source="Supervisor Resolution",
                finding=(
                    "REVIEW because the disagreement contains a "
                    "blocking evidence or safety risk."
                ),
                confidence=0.95,
                evidence_refs=[
                    "blocking_disagreement",
                ],
            )
        )
    elif caution_disagreements and supervisor_recommendation == "APPLY":
        topics = "; ".join(caution_disagreements)

        findings.append(
            SupervisorFinding(
                source="Supervisor Resolution",
                finding=(
                    f"APPLY is retained because the disagreement "
                    f"concerns a non-blocking risk ({topics}). "
                    "The opportunity may proceed, but unverified "
                    "SaaS, CRM, or account-ownership experience must "
                    "not be represented as verified experience."
                ),
                confidence=0.90,
                evidence_refs=[
                    "non_blocking_risk",
                    "candidate_truth",
                ],
            )
        )
    elif supervisor_recommendation == "SKIP":
        findings.append(
            SupervisorFinding(
                source="Supervisor Resolution",
                finding=(
                    "SKIP because the opportunity does not justify "
                    "further application effort."
                ),
                confidence=0.95,
                evidence_refs=[
                    "opportunity_priority",
                ],
            )
        )
    else:
        findings.append(
            SupervisorFinding(
                source="Supervisor Resolution",
                finding=(
                    "REVIEW because the available agent findings "
                    "do not support a safe final recommendation."
                ),
                confidence=0.80,
                evidence_refs=[
                    "unresolved_agent_findings",
                ],
            )
        )

    # --------------------------------------------------
    # Confidence
    # --------------------------------------------------

    confidence_values = [
        finding.confidence
        for finding in findings
    ]

    if confidence_values:
        confidence = (
            sum(confidence_values)
            / len(confidence_values)
        )
    else:
        confidence = 0.0

    if hard_blockers:
        confidence *= 0.70
    elif caution_disagreements:
        confidence *= 0.85

    if unresolved_questions:
        confidence *= 0.95

    confidence = round(
        min(max(confidence, 0.0),
            1.0),
        4,
    )

    return SupervisorDecision(
        job_id=case.job_id,
        company=case.company,
        title=case.title,
        recommendation=supervisor_recommendation,
        confidence=confidence,
        findings=findings,
        conflicts=conflicts,
        unresolved_questions=unresolved_questions,
        human_review_required=True,
        external_action_allowed=False,
    )
