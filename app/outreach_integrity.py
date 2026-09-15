import hashlib
import json

from app.models.outreach_message import OutreachMessage


def calculate_outreach_hash(
    message: OutreachMessage,
) -> str:
    content = {
        "job_id": message.job_id,
        "company": message.company,
        "title": message.title,
        "channel": message.channel,
        "subject": message.subject,
        "body": message.body,
        "evidence_ids": message.evidence_ids,
        "claims_safe": message.claims_safe,
        "safety_reason": message.safety_reason,
    }

    serialized = json.dumps(
        content,
        sort_keys=True,
        separators=(",", ":"),
    )

    return hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()
