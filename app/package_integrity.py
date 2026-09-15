import hashlib
import json

from app.models.application_package import ApplicationPackage


def calculate_content_hash(package: ApplicationPackage) -> str:
    """
    Create a deterministic SHA-256 fingerprint of the application content.

    Human approval metadata is deliberately excluded because changing
    approval status or reviewer notes must not change the content identity.
    """

    content = {
        "job_id": package.job_id,
        "company": package.company,
        "title": package.title,
        "application_decision": package.application_decision,
        "profile": package.profile.model_dump(mode="json"),
        "evidence_map": [
            item.model_dump(mode="json")
            for item in package.evidence_map
        ],
        "resume": package.resume.model_dump(mode="json"),
        "claims_safe": package.claims_safe,
        "resume_ready": package.resume_ready,
        "cover_letter_ready": package.cover_letter_ready,
        "outreach_ready": package.outreach_ready,
        "forbidden_claims": package.forbidden_claims,
        "critical_gaps": package.critical_gaps,
        "core_gaps": package.core_gaps,
    }

    canonical_content = json.dumps(
        content,
        sort_keys=True,
        separators=(",", ":"),
    )

    return hashlib.sha256(
        canonical_content.encode("utf-8")
    ).hexdigest()
