from app.models.job import Job
from app.models.career_strategy import CareerStrategy
from app.capability_map import CAPABILITY_RELATIONSHIPS
from app.company_strategic_fit import calculate_company_strategic_fit


def calculate_role_alignment(
    job: Job,
    strategy: CareerStrategy
) -> float:
    """
    Measure how closely the job title aligns with
    the candidate's target roles.
    """

    job_title = job.title.lower()

    for target_role in strategy.target_roles:

        target = target_role.lower()

        if target in job_title or job_title in target:
            return 100.0

    if "customer success" in job_title:
        return 80.0

    return 30.0


def calculate_capability_alignment(
    job: Job,
    strategy: CareerStrategy
) -> float:
    """
    Measure alignment between job requirements and
    the candidate's strategic capabilities.

    Exact matches receive full credit.

    Related capabilities receive partial credit.
    """

    priority_capabilities = {
        capability.lower()
        for capability in strategy.priority_capabilities
    }

    total_score = 0.0

    for requirement in job.requirements:

        requirement_name = requirement.name.lower()

        # Exact capability match.
        if requirement_name in priority_capabilities:
            total_score += 1.0
            continue

        # Related capability match.
        related_capabilities = (
            CAPABILITY_RELATIONSHIPS.get(
                requirement_name,
                []
            )
        )

        related_match = any(
            capability in priority_capabilities
            for capability in related_capabilities
        )

        if related_match:
            total_score += 0.5

    total_requirements = len(job.requirements)

    if total_requirements == 0:
        return 0.0

    return (
        total_score / total_requirements
    ) * 100


def calculate_critical_gap_penalty(
    fit_result: dict
) -> float:
    """
    Penalize opportunities with critical requirements
    that are not currently supported by candidate evidence.
    """

    critical_gaps = len(
        fit_result.get("critical_gaps", [])
    )

    return critical_gaps * 20.0


def calculate_opportunity_score(
    job: Job,
    strategy: CareerStrategy,
    fit_result: dict,
    company_intelligence=None,
):
    """
    Calculate the strategic value of an opportunity.

    Fit asks:
        Can the candidate satisfy the job?

    Opportunity asks:
        Is the job worth prioritizing?
    """

    fit_score = fit_result["overall_score"]

    role_alignment = calculate_role_alignment(
        job,
        strategy
    )

    capability_alignment = calculate_capability_alignment(
        job,
        strategy
    )

    critical_gap_penalty = calculate_critical_gap_penalty(
        fit_result
    )

    company_strategic_fit = None

    if company_intelligence is not None:
        company_strategic_fit = calculate_company_strategic_fit(
            company_intelligence,
            strategy,
        )

    raw_score = (
        fit_score * 0.50
        + role_alignment * 0.25
        + capability_alignment * 0.25
    )

    opportunity_score = max(
        raw_score - critical_gap_penalty,
        0
    )

    if opportunity_score >= 75:
        priority = "HIGH"

    elif opportunity_score >= 55:
        priority = "MEDIUM"

    else:
        priority = "LOW"

    if priority == "HIGH":

        recommendation = (
            "Strong strategic opportunity. "
            "Prioritize application preparation and networking."
        )

    elif priority == "MEDIUM":

        recommendation = (
            "Potentially worthwhile opportunity. "
            "Review critical gaps before investing significant "
            "application effort."
        )

    else:

        recommendation = (
            "Low strategic priority. "
            "Consider only if additional information improves "
            "the opportunity assessment."
        )

    return {
        "job_id": job.job_id,
        "company": job.company,
        "title": job.title,

        "opportunity_score": round(
            opportunity_score,
            2
        ),

        "priority": priority,
        "company_strategic_fit": company_strategic_fit,

        "components": {
            "candidate_fit": round(
                fit_score,
                2
            ),

            "role_alignment": round(
                role_alignment,
                2
            ),

            "capability_alignment": round(
                capability_alignment,
                2
            ),

            "critical_gap_penalty": round(
                critical_gap_penalty,
                2
            )
        },

        "recommendation": recommendation,
    }
