import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.application_execution_service import execute_application
from app.careeros import load_existing_application_package
from app.models.execution_authorization import ExecutionAuthorization
from app.models.opportunity_status import OpportunityStatus
from app.package_integrity import calculate_content_hash


class RecordingAdapter:

    def __init__(self):
        self.called = False

    def submit_application(self, package, authorization):
        self.called = True

        from app.models.execution_result import ExecutionResult

        return ExecutionResult(
            job_id=package.job_id,
            company=package.company,
            title=package.title,
            action="APPLICATION_SUBMISSION",
            execution_status="SIMULATED",
            package_version=package.package_version,
            content_hash=package.content_hash,
            executed_at="TEST",
            external_reference="TEST-REF",
            message="Test application submission.",
        )


class ApplicationExecutionServiceTest(unittest.TestCase):

    def _approved_package(self):
        package = load_existing_application_package("JOB-001")
        self.assertIsNotNone(package)

        package = copy.deepcopy(package)

        package.status = OpportunityStatus.APPROVED
        package.approved_by_human = True
        package.content_hash = calculate_content_hash(package)
        package.approved_content_hash = package.content_hash

        return package

    def _authorization(self, package):
        return ExecutionAuthorization(
            job_id=package.job_id,
            company=package.company,
            title=package.title,
            package_version=package.package_version,
            approved_content_hash=package.content_hash,
        )

    def test_unauthorized_application_never_reaches_adapter(self):
        package = self._approved_package()
        authorization = self._authorization(package)
        adapter = RecordingAdapter()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_package_dir = Path(temp_dir) / "applications"
            temp_package_dir.mkdir()

            with patch(
                "app.application_execution_service.PACKAGE_DIR",
                temp_package_dir,
            ):
                result = execute_application(
                    package,
                    authorization,
                    adapter,
                )

        self.assertEqual(result.execution_status, "BLOCKED")
        self.assertFalse(adapter.called)
        self.assertEqual(
            package.status,
            OpportunityStatus.APPROVED,
        )

    def test_authorized_application_reaches_adapter(self):
        package = self._approved_package()
        authorization = self._authorization(package)

        authorization.authorize(
            application_submission=True,
        )

        adapter = RecordingAdapter()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_package_dir = Path(temp_dir) / "applications"
            temp_package_dir.mkdir()

            with patch(
                "app.application_execution_service.PACKAGE_DIR",
                temp_package_dir,
            ), patch(
                "app.application_execution_service.save_application_record"
            ) as mock_save_crm:

                result = execute_application(
                    package,
                    authorization,
                    adapter,
                )

                mock_save_crm.assert_called_once()

        self.assertEqual(
            result.execution_status,
            "SIMULATED",
        )
        self.assertTrue(adapter.called)
        self.assertEqual(
            package.status,
            OpportunityStatus.APPLIED,
        )
        self.assertIsNotNone(result.external_reference)
        self.assertEqual(result.external_reference, "TEST-REF")


if __name__ == "__main__":
    unittest.main()
