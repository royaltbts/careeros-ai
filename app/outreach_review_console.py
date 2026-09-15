from app.models.outreach_review import OutreachReview


def display_outreach_review(
    review: OutreachReview,
) -> None:
    recommendation = review.recommendation
    message = review.message

    print("=" * 60)
    print("             OUTREACH REVIEW")
    print("=" * 60)

    print(f"Job: {review.job_id}")
    print(f"Company: {review.company}")
    print(f"Title: {review.title}")

    print("\n--- FOLLOW-UP RECOMMENDATION ---")
    print(f"Recommendation: {recommendation.recommendation}")
    print(f"Priority: {recommendation.priority}")
    print(f"Reason: {recommendation.reason}")

    if recommendation.days_since_last_event is not None:
        print(
            "Days since event:",
            round(recommendation.days_since_last_event, 1),
        )

    print(
        "Trigger:",
        recommendation.triggering_event_type or "N/A",
    )

    print("\n--- MESSAGE ---")
    print(f"Channel: {message.channel}")
    print(f"Subject: {message.subject}")
    print("\n" + message.body)

    print("--- EVIDENCE ---")
    print(
        "Evidence IDs:",
        ", ".join(message.evidence_ids)
        if message.evidence_ids
        else "None",
    )

    print("\n--- SAFETY ---")
    print(f"Claims safe: {message.claims_safe}")
    print(f"Safety reason: {message.safety_reason}")

    print("\n--- APPROVAL ---")
    print(f"Decision: {review.decision}")
    print(f"Human approved: {review.approved_by_human}")

    print("=" * 60)
