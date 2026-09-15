import unittest

from app.models.outreach_authorization import OutreachAuthorization
from app.models.outreach_message import OutreachMessage
from app.outreach_authorizer import (
    can_execute_outreach,
    outreach_block_reason,
)
from app.outreach_integrity import calculate_outreach_hash


class OutreachAuthorizationTest(unittest.TestCase):

    def _message(self, version=1):
        return OutreachMessage(
            package_version=version,
            job_id="TEST-001",
            company="Test Company",
            title="Customer Success Manager",
            channel="EMAIL",
            subject="Following up",
            body="Hello, I wanted to follow up regarding the opportunity.",
            evidence_ids=["EV001"],
            claims_safe=True,
        )

    def test_matching_version_is_authorized(self):
        message = self._message(version=1)

        authorization = OutreachAuthorization(
            job_id=message.job_id,
            company=message.company,
            title=message.title,
            recommendation="REVIEW_OUTREACH",
            package_version=1,
            content_hash=calculate_outreach_hash(message),
        )

        authorization.authorize()

        self.assertTrue(
            can_execute_outreach(
                message,
                authorization,
            )
        )

    def test_version_mismatch_blocks_outreach(self):
        message = self._message(version=2)

        authorization = OutreachAuthorization(
            job_id=message.job_id,
            company=message.company,
            title=message.title,
            recommendation="REVIEW_OUTREACH",
            package_version=1,
            content_hash=calculate_outreach_hash(message),
        )

        authorization.authorize()

        self.assertFalse(
            can_execute_outreach(
                message,
                authorization,
            )
        )

        self.assertIn(
            "version does not match",
            outreach_block_reason(
                message,
                authorization,
            ),
        )


if __name__ == "__main__":
    unittest.main()
