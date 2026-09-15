from enum import Enum


class OpportunityStatus(str, Enum):

    NEW = "NEW"

    ANALYZED = "ANALYZED"

    PENDING_APPROVAL = "PENDING_APPROVAL"

    APPROVED = "APPROVED"

    REJECTED = "REJECTED"

    APPLIED = "APPLIED"

    INTERVIEW = "INTERVIEW"

    OFFER = "OFFER"

    ACCEPTED = "ACCEPTED"
