from app.models.opportunity_status import OpportunityStatus
from app.opportunity_workflow import transition_status
from app.human_approval import prepare_for_approval


def request_human_approval(job_id: str):
    """
    Prepare an opportunity for human approval.

    The opportunity enters PENDING_APPROVAL.
    No external action is permitted.
    """

    approval = prepare_for_approval(
        job_id
    )

    if not approval.resume_ready:
        raise ValueError(
            "Application package is not ready "
            "for human approval."
        )

    if not approval.claims_safe:
        raise ValueError(
            "Application contains unsafe claims."
        )

    status = transition_status(
        OpportunityStatus.ANALYZED,
        OpportunityStatus.PENDING_APPROVAL
    )

    return approval, status


def approve_application(
    approval,
    current_status: OpportunityStatus
):
    """
    Approve an application only through
    an explicit human decision.
    """

    if current_status != OpportunityStatus.PENDING_APPROVAL:
        raise ValueError(
            "Application can only be approved "
            "from PENDING_APPROVAL."
        )

    approval.decision = "APPROVED"
    approval.approved_by_human = True

    new_status = transition_status(
        current_status,
        OpportunityStatus.APPROVED
    )

    return approval, new_status


def reject_application(
    approval,
    current_status: OpportunityStatus,
    reason: str
):
    """
    Reject an application through an explicit
    human decision.
    """

    if current_status != OpportunityStatus.PENDING_APPROVAL:
        raise ValueError(
            "Application can only be rejected "
            "from PENDING_APPROVAL."
        )

    approval.decision = "REJECTED"
    approval.approved_by_human = False
    approval.reviewer_notes = reason

    new_status = transition_status(
        current_status,
        OpportunityStatus.REJECTED
    )

    return approval, new_status


def main():

    print()
    print("=" * 80)
    print("CAREEROS HUMAN APPROVAL WORKFLOW")
    print("=" * 80)

    # --------------------------------------------------
    # Step 1 — Prepare application
    # --------------------------------------------------

    approval, status = request_human_approval(
        "JOB-001"
    )

    print()
    print("APPLICATION PREPARED")
    print("-" * 80)

    print(
        f"Company: "
        f"{approval.company}"
    )

    print(
        f"Role: "
        f"{approval.title}"
    )

    print(
        f"Status: "
        f"{status.value}"
    )

    print(
        f"Decision: "
        f"{approval.decision}"
    )

    print(
        f"Human approval: "
        f"{approval.approved_by_human}"
    )

    # --------------------------------------------------
    # Step 2 — Explicit human approval
    # --------------------------------------------------

    approval, status = approve_application(
        approval,
        status
    )

    print()
    print("HUMAN APPROVAL")
    print("-" * 80)

    print(
        f"Status: "
        f"{status.value}"
    )

    print(
        f"Decision: "
        f"{approval.decision}"
    )

    print(
        f"Human approval: "
        f"{approval.approved_by_human}"
    )

    print()
    print("=" * 80)
    print("HUMAN APPROVAL WORKFLOW COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()

