from app.models.application_record import ApplicationRecord
from app.models.outreach_message import OutreachMessage
from app.follow_up_recommender import (
    create_follow_up_recommendation,
)
from app.outreach_evidence import select_outreach_evidence
from app.claim_safety import run_safety_gate


def generate_follow_up_message(
    record: ApplicationRecord,
    threshold_days: int = 7,
) -> OutreachMessage:
    """
    Generate a deterministic follow-up message.

    This function only drafts content.
    It does not authorize or send outreach.
    """

    recommendation = create_follow_up_recommendation(
        record,
        threshold_days,
    )

    if recommendation.recommendation != "REVIEW_OUTREACH":
        raise ValueError(
            "Outreach message should only be generated "
            "when the follow-up recommendation is REVIEW_OUTREACH."
        )

    selected_evidence = select_outreach_evidence(
        [
            "Customer Communication",
            "Customer Experience",
            "Continuous Improvement",
        ]
    )

    evidence_ids = [
        item.id
        for item in selected_evidence
    ]

    subject = (
        f"Following up on the {record.title} opportunity"
    )

    body = (
        f"Hello,\n\n"
        f"I wanted to follow up regarding the "
        f"{record.title} opportunity at {record.company}. "
        f"I remain very interested in the opportunity, "
        f"particularly because it aligns well with my "
        f"experience in customer and stakeholder communication, "
        f"customer experience metrics, and continuous improvement.\n\n"
        f"I would be happy to provide any additional "
        f"information needed.\n\n"
        f"Thank you for your time and consideration.\n"
    )

    safety_result = run_safety_gate(
        record.job_id,
        [
            {
                "claim": (
                    "My experience in customer and stakeholder "
                    "communication, customer experience metrics, "
                    "and continuous improvement aligns well with "
                    "this opportunity."
                ),
                "evidence_ids": evidence_ids,
            }
        ],
    )

    if not safety_result.all_claims_safe:
        raise ValueError(
            "Outreach message failed the Claim Safety Gate."
        )

    safety_reason = (
        safety_result.checks[0].reason
        if safety_result.checks
        else "Claim Safety Gate passed."
    )

    return OutreachMessage(
        job_id=record.job_id,
        company=record.company,
        title=record.title,
        channel="EMAIL",
        subject=subject,
        body=body,
        evidence_ids=evidence_ids,
        claims_safe=safety_result.all_claims_safe,
        safety_reason=safety_reason,
        human_review_required=True,
        approved_by_human=False,
    )
