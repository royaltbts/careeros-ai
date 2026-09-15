from app.models.opportunity_status import OpportunityStatus


ALLOWED_TRANSITIONS = {

    OpportunityStatus.NEW: [
        OpportunityStatus.ANALYZED,
        OpportunityStatus.REJECTED
    ],

    OpportunityStatus.ANALYZED: [
        OpportunityStatus.PENDING_APPROVAL,
        OpportunityStatus.REJECTED
    ],

    OpportunityStatus.PENDING_APPROVAL: [
        OpportunityStatus.APPROVED,
        OpportunityStatus.REJECTED
    ],

    OpportunityStatus.APPROVED: [
        OpportunityStatus.APPLIED,
        OpportunityStatus.REJECTED,
        OpportunityStatus.PENDING_APPROVAL
    ],

    OpportunityStatus.APPLIED: [
        OpportunityStatus.INTERVIEW,
        OpportunityStatus.REJECTED
    ],

    OpportunityStatus.INTERVIEW: [
        OpportunityStatus.OFFER,
        OpportunityStatus.REJECTED
    ],

    OpportunityStatus.OFFER: [
        OpportunityStatus.ACCEPTED,
        OpportunityStatus.REJECTED
    ],

    OpportunityStatus.ACCEPTED: [],

    OpportunityStatus.REJECTED: []
}


def can_transition(
    current_status: OpportunityStatus,
    new_status: OpportunityStatus
) -> bool:

    """
    Check whether an opportunity is allowed to move
    from its current state to the requested state.
    """

    return new_status in ALLOWED_TRANSITIONS.get(
        current_status,
        []
    )


def transition_status(
    current_status: OpportunityStatus,
    new_status: OpportunityStatus
) -> OpportunityStatus:

    """
    Perform a validated opportunity status transition.

    Raises ValueError if the transition is not allowed.
    """

    if not can_transition(
        current_status,
        new_status
    ):

        raise ValueError(
            f"Invalid opportunity transition: "
            f"{current_status.value} -> "
            f"{new_status.value}"
        )

    return new_status
