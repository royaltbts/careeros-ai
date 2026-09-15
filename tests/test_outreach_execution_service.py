import unittest

from app.models.outreach_authorization import OutreachAuthorization
from app.models.outreach_message import OutreachMessage
from app.outreach_execution_service import execute_outreach
from app.outreach_integrity import calculate_outreach_hash


class RecordingOutreachAdapter:

    def __init__(self):
        self.called = False

    def send_outreach(self, message, authorization):
        self.called = True

        from app.models.outreach_execution_result import (
            OutreachExecutionResult,
        )

        return OutreachExecutionResult(
            job_id=message.job_id,
            company=message.company,
            title=message.title,
            channel=message.channel,
            action="OUTREACH",
            execution_status="SIMULATED",
            package_version=message.package_version,
            content_hash=calculate_outreach_hash(message),
            executed_at="TEST",
            external_reference="TEST-OUTREACH-REF",
            message="Test outreach simulated.",
        )


class OutreachExecutionServiceTest(unittest.TestCase):

    def _message(self):
        return OutreachMessage(
            package_version=1,
            job_id="TEST-001",
            company="Test Company",
            title="Customer Success Manager",
            channel="EMAIL",
            subject="Following up",
            body=(
                "Hello, I wanted to follow up regarding "
                "the opportunity."
            ),
            evidence_ids=["EV001"],
            claims_safe=True,
        )

    def _authorization(self, message):
        return OutreachAuthorization(
            job_id=message.job_id,
            company=message.company,
            title=message.title,
            recommendation="REVIEW_OUTREACH",
            package_version=message.package_version,
            content_hash=calculate_outreach_hash(message),
        )

    def test_unauthorized_outreach_never_reaches_adapter(self):
        message = self._message()
        authorization = self._authorization(message)
        adapter = RecordingOutreachAdapter()

        result = execute_outreach(
            message,
            authorization,
            adapter,
        )

        self.assertEqual(
            result.execution_status,
            "BLOCKED",
        )
        self.assertFalse(adapter.called)

    def test_authorized_outreach_reaches_adapter(self):
        message = self._message()
        authorization = self._authorization(message)

        authorization.authorize(
            reviewer_notes="Approved for testing.",
        )

        adapter = RecordingOutreachAdapter()

        result = execute_outreach(
            message,
            authorization,
            adapter,
        )

        self.assertEqual(
            result.execution_status,
            "SIMULATED",
        )
        self.assertTrue(adapter.called)

    def test_tampered_outreach_never_reaches_adapter(self):
        message = self._message()
        authorization = self._authorization(message)

        authorization.authorize(
            reviewer_notes="Approved for testing.",
        )

        message.body += " Unauthorized modification."

        adapter = RecordingOutreachAdapter()

        result = execute_outreach(
            message,
            authorization,
            adapter,
        )

        self.assertEqual(
            result.execution_status,
            "BLOCKED",
        )
        self.assertFalse(adapter.called)


if __name__ == "__main__":
    unittest.main()
