from app.models.outreach_message import OutreachMessage
from app.outreach_integrity import calculate_outreach_hash
from app.models.outreach_authorization import OutreachAuthorization


def can_execute_outreach(
    message: OutreachMessage,
    authorization: OutreachAuthorization,
) -> bool:
    if authorization.authorization_status != "AUTHORIZED":
        return False

    if not authorization.approved_by_human:
        return False

    if not authorization.outreach_authorized:
        return False

    if authorization.job_id != message.job_id:
        return False

    if authorization.package_version != message.package_version:
        return False

    if authorization.content_hash != calculate_outreach_hash(message):
        return False

    return True


def outreach_block_reason(
    message: OutreachMessage,
    authorization: OutreachAuthorization,
) -> str:
    if authorization.authorization_status != "AUTHORIZED":
        return "Outreach authorization is not AUTHORIZED."

    if not authorization.approved_by_human:
        return "Human approval is missing."

    if not authorization.outreach_authorized:
        return "Outreach permission has not been granted."

    if authorization.job_id != message.job_id:
        return "Authorization job ID does not match the outreach message."

    if authorization.package_version != message.package_version:
        return "Authorization package version does not match the outreach message."

    if authorization.content_hash != calculate_outreach_hash(message):
        return "Authorization content hash does not match the outreach message."

    return "Outreach is authorized."
