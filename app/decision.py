from app.models.job import Job


def calculate_evidence_confidence(
    classification: str,
    criticality: str
) -> str:
    """
    Describe how strongly our evidence supports a requirement.

    HIGH:
        Verified direct evidence exists.

    MEDIUM:
        Related verified evidence exists, but the match
        requires interpretation.

    UNKNOWN:
        The evidence library does not currently establish
        the requirement.

    IMPORTANT:
        UNKNOWN does NOT mean the candidate lacks the skill.
        It only means our current evidence does not establish it.
    """

    if classification == "DIRECT":
        return "HIGH"

    if classification == "TRANSFERABLE":
        return "MEDIUM"

    return "UNKNOWN"


def make_application_decision(
    job: Job,
    fit_result: dict
):
    """
    Convert the scoring result into an actionable
    application recommendation.
    """

    overall_score = fit_result["overall_score"]

    critical_gaps = fit_result["critical_gaps"]
    core_gaps = fit_result["core_gaps"]

    requirement_analysis = fit_result[
        "requirement_analysis"
    ]

    # ---------------------------------------------------------
    # EVIDENCE CONFIDENCE ANALYSIS
    # ---------------------------------------------------------

    confidence_summary = {
        "HIGH": 0,
        "MEDIUM": 0,
        "UNKNOWN": 0
    }

    for match in requirement_analysis:

        evidence_confidence = calculate_evidence_confidence(
            match["match_type"],
            match["criticality"]
        )

        match["evidence_confidence"] = evidence_confidence

        confidence_summary[evidence_confidence] += 1

    # ---------------------------------------------------------
    # APPLICATION DECISION
    # ---------------------------------------------------------

    if critical_gaps:

        apply_decision = "CONDITIONAL"
        priority = "MEDIUM"

        reason = (
            "A critical requirement is missing. "
            "The opportunity may still be worth pursuing "
            "because the candidate has substantial transferable "
            "and direct experience, but human review is required."
        )

    elif overall_score >= 75:

        apply_decision = "YES"
        priority = "HIGH"

        reason = (
            "Strong evidence-backed fit with no critical "
            "requirements missing."
        )

    elif overall_score >= 55:

        apply_decision = "YES"
        priority = "MEDIUM"

        reason = (
            "Reasonable fit with some gaps. "
            "Application may be worthwhile if the role "
            "aligns with the candidate's career strategy."
        )

    else:

        apply_decision = "NO"
        priority = "LOW"

        reason = (
            "The evidence-backed fit is currently too weak "
            "to justify prioritizing the opportunity."
        )

    # ---------------------------------------------------------
    # NETWORKING RECOMMENDATION
    # ---------------------------------------------------------

    if critical_gaps:
        networking = "HIGHLY RECOMMENDED"

    elif priority == "HIGH":
        networking = "RECOMMENDED"

    else:
        networking = "OPTIONAL"

    # ---------------------------------------------------------
    # TAILORING RECOMMENDATION
    # ---------------------------------------------------------

    if apply_decision in ["YES", "CONDITIONAL"]:

        resume_tailoring = "REQUIRED"
        cover_letter = "RECOMMENDED"

    else:

        resume_tailoring = "NOT REQUIRED"
        cover_letter = "NOT REQUIRED"

    # ---------------------------------------------------------
    # HUMAN APPROVAL
    # ---------------------------------------------------------

    human_approval = "REQUIRED"

    # ---------------------------------------------------------
    # RETURN DECISION
    # ---------------------------------------------------------

    return {
        "job_id": job.job_id,
        "company": job.company,
        "title": job.title,

        "fit_score": overall_score,

        "decision": {
            "apply": apply_decision,
            "priority": priority,
            "reason": reason
        },

        "confidence": confidence_summary,

        "strategy": {
            "resume_tailoring": resume_tailoring,
            "cover_letter": cover_letter,
            "networking": networking
        },

        "critical_gaps": critical_gaps,
        "core_gaps": core_gaps,

        "human_approval": human_approval,

        "requirement_analysis": requirement_analysis
    }
