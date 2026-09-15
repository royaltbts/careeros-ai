from app.models.outreach_review import OutreachReview
from app.outreach_integrity import calculate_outreach_hash


def approve_outreach(
    review: OutreachReview,
    reviewer_notes: str | None = None,
) -> OutreachReview:

    if review.decision != "PENDING":
        raise ValueError(
            f"Cannot approve outreach review in state: "
            f"{review.decision}"
        )

    if not review.message.claims_safe:
        raise ValueError(
            "Cannot approve outreach because the message "
            "failed the Claim Safety Gate."
        )

    review.decision = "APPROVED"
    review.approved_by_human = True
    review.message.approved_by_human = True
    review.approved_content_hash = calculate_outreach_hash(
        review.message
    )
    review.reviewer_notes = reviewer_notes

    return review


def reject_outreach(
    review: OutreachReview,
    reason: str,
) -> OutreachReview:

    if review.decision != "PENDING":
        raise ValueError(
            f"Cannot reject outreach review in state: "
            f"{review.decision}"
        )

    review.decision = "REJECTED"
    review.approved_by_human = False
    review.message.approved_by_human = False
    review.reviewer_notes = reason

    return review
