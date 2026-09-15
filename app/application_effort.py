from app.models.application_effort import ApplicationEffort


def determine_effort_level(
    recommendation: str,
    opportunity_score: float,
) -> tuple[str, str, list[str]]:

    if recommendation == "SKIP":
        return (
            "NONE",
            "Opportunity is below the current pursuit threshold.",
            [],
        )

    if recommendation == "CONDITIONAL":
        return (
            "LIMITED",
            "Opportunity has evidence gaps that should be resolved before significant application effort.",
            [
                "Review critical gaps",
                "Validate whether gaps are genuinely disqualifying",
            ],
        )

    if recommendation == "REVIEW":
        return (
            "TARGETED",
            "Opportunity deserves review, but does not yet justify full application effort.",
            [
                "Review role fit",
                "Review company intelligence",
            ],
        )

    if opportunity_score >= 90:
        return (
            "FULL",
            "Very strong opportunity with sufficient evidence to justify substantial application effort.",
            [
                "Tailor resume",
                "Prepare cover letter",
                "Research company",
                "Identify networking opportunities",
                "Prepare interview evidence",
            ],
        )

    return (
        "TARGETED",
        "Strong opportunity, but below the threshold for maximum application effort.",
        [
            "Tailor resume",
            "Review company intelligence",
            "Identify networking opportunities",
        ],
    )


def build_application_effort(
    decision,
) -> ApplicationEffort:

    level, reason, actions = determine_effort_level(
        decision.recommendation,
        decision.opportunity_score,
    )

    return ApplicationEffort(
        job_id=decision.job_id,
        company=decision.company,
        title=decision.title,
        recommendation=decision.recommendation,
        opportunity_score=decision.opportunity_score,
        effort_level=level,
        effort_reason=reason,
        recommended_actions=actions,
    )
