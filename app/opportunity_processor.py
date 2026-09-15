from app.models.job_opportunity import JobOpportunity


def update_opportunity(
    opportunity: JobOpportunity,
    fit_result: dict,
    opportunity_result: dict,
    decision_result: dict
) -> JobOpportunity:
    """
    Update a job opportunity with its analysis results.

    This function does not approve or submit an application.
    Human approval remains a separate action.
    """

    opportunity.fit_score = fit_result["overall_score"]

    opportunity.opportunity_score = (
        opportunity_result["opportunity_score"]
    )

    opportunity.priority = (
        opportunity_result["priority"]
    )

    opportunity.application_decision = (
        decision_result["decision"]["apply"]
    )

    opportunity.status = "ANALYZED"

    # Never automatically approve an opportunity.
    opportunity.human_approval = False

    return opportunity
