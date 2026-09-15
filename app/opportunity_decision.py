from app.models.opportunity_decision import OpportunityDecision


def build_opportunity_decision(
    opportunity: dict,
) -> OpportunityDecision:
    """
    Convert an opportunity ranking into an auditable
    application-priority decision.

    This function does not recalculate the opportunity score.
    It interprets existing scoring and evidence signals.
    """

    priority = opportunity["priority"]
    critical_gaps = opportunity.get("critical_gaps", [])
    core_gaps = opportunity.get("core_gaps", [])

    strategic_fit = opportunity.get(
        "company_strategic_fit"
    ) or {}

    strategic_alignment = strategic_fit.get(
        "strategic_alignment"
    )
    research_confidence = strategic_fit.get(
        "research_confidence"
    )
    research_coverage = strategic_fit.get(
        "research_coverage"
    )
    research_evidence_confidence = strategic_fit.get(
        "research_evidence_confidence"
    )
    research_quality = strategic_fit.get(
        "research_quality"
    )
    decision_ready_fit = strategic_fit.get(
        "decision_ready_fit"
    )

    strengths = []

    if opportunity.get("fit_score", 0) >= 80:
        strengths.append("Strong candidate fit")
    elif opportunity.get("fit_score", 0) >= 60:
        strengths.append("Moderate candidate fit")

    if priority == "HIGH":
        strengths.append("High strategic opportunity priority")

    if strategic_alignment is not None:
        if strategic_alignment >= 75:
            strengths.append(
                "Strong company strategic alignment"
            )
        elif strategic_alignment >= 50:
            strengths.append(
                "Moderate company strategic alignment"
            )

    reasons = []

    if not critical_gaps:
        reasons.append(
            "No critical evidence gaps"
        )
    else:
        reasons.append(
            f"{len(critical_gaps)} critical evidence gap(s) "
            "require review"
        )

    if core_gaps:
        reasons.append(
            f"{len(core_gaps)} core capability gap(s) "
            "should be reviewed"
        )

    if research_confidence is not None:
        if research_confidence >= 90:
            reasons.append(
                "Company research has high confidence"
            )
        elif research_confidence >= 75:
            reasons.append(
                "Company research has moderate confidence"
            )
        else:
            reasons.append(
                "Company research confidence is limited"
            )

    if priority == "LOW":
        recommendation = "SKIP"
    elif critical_gaps:
        recommendation = "CONDITIONAL"
    elif priority == "HIGH":
        if (
            research_confidence is not None
            and research_confidence < 75
        ):
            recommendation = "REVIEW"
        else:
            recommendation = "APPLY"
    else:
        recommendation = "REVIEW"

    if recommendation == "APPLY":
        reasons.append(
            "Opportunity meets the current application "
            "priority threshold"
        )
    elif (
        recommendation == "REVIEW"
        and priority == "HIGH"
        and research_confidence is not None
        and research_confidence < 75
        and not critical_gaps
    ):
        reasons.append(
            "High-priority opportunity requires stronger "
            "company research before application effort"
        )
    elif recommendation == "REVIEW":
        reasons.append(
            "Opportunity warrants additional review "
            "before significant application effort"
        )
    elif recommendation == "SKIP":
        reasons.append(
            "Opportunity is below the current strategic "
            "priority threshold"
        )

    transferable = []

    if core_gaps:
        transferable.extend(core_gaps)

    return OpportunityDecision(
        job_id=opportunity["job_id"],
        company=opportunity["company"],
        title=opportunity["title"],
        opportunity_score=opportunity["opportunity_score"],
        priority=priority,
        recommendation=recommendation,
        decision_reasons=reasons,
        strengths=strengths,
        critical_gaps=critical_gaps,
        transferable_opportunities=transferable,
        company_strategic_alignment=strategic_alignment,
        company_research_confidence=research_confidence,
        company_research_coverage=research_coverage,
        company_research_evidence_confidence=(
            research_evidence_confidence
        ),
        company_research_quality=research_quality,
        company_decision_ready_fit=decision_ready_fit,
        human_review_required=True,
    )
