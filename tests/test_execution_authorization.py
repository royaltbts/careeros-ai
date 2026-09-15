import copy
import unittest

from app.careeros import load_existing_application_package
from app.execution_authorizer import (
    can_execute_action,
    authorization_block_reason,
)
from app.models.execution_authorization import ExecutionAuthorization
from app.models.opportunity_status import OpportunityStatus
from app.package_integrity import calculate_content_hash


class ExecutionAuthorizationTest(unittest.TestCase):

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

    def test_pending_authorization_blocks_application_submission(self):
        package = self._approved_package()
        authorization = self._authorization(package)

        self.assertFalse(
            can_execute_action(
                package,
                authorization,
                "APPLICATION_SUBMISSION",
            )
        )

        self.assertIn(
            "not active",
            authorization_block_reason(
                package,
                authorization,
                "APPLICATION_SUBMISSION",
            ),
        )

    def test_human_can_authorize_application_submission(self):
        package = self._approved_package()
        authorization = self._authorization(package)

        authorization.authorize(
            application_submission=True,
            outreach=False,
        )

        self.assertTrue(
            can_execute_action(
                package,
                authorization,
                "APPLICATION_SUBMISSION",
            )
        )

        self.assertFalse(
            can_execute_action(
                package,
                authorization,
                "OUTREACH",
            )
        )

    def test_human_can_authorize_outreach_without_application(self):
        package = self._approved_package()
        authorization = self._authorization(package)

        authorization.authorize(
            application_submission=False,
            outreach=True,
        )

        self.assertFalse(
            can_execute_action(
                package,
                authorization,
                "APPLICATION_SUBMISSION",
            )
        )

        self.assertTrue(
            can_execute_action(
                package,
                authorization,
                "OUTREACH",
            )
        )

    def test_wrong_package_version_blocks_action(self):
        package = self._approved_package()
        authorization = self._authorization(package)

        authorization.authorize(
            application_submission=True,
        )

        authorization.package_version += 1

        self.assertFalse(
            can_execute_action(
                package,
                authorization,
                "APPLICATION_SUBMISSION",
            )
        )

        self.assertIn(
            "version does not match",
            authorization_block_reason(
                package,
                authorization,
                "APPLICATION_SUBMISSION",
            ),
        )

    def test_wrong_content_hash_blocks_action(self):
        package = self._approved_package()
        authorization = self._authorization(package)

        authorization.authorize(
            application_submission=True,
        )

        authorization.approved_content_hash = "tampered-hash"

        self.assertFalse(
            can_execute_action(
                package,
                authorization,
                "APPLICATION_SUBMISSION",
            )
        )

        self.assertIn(
            "hash does not match",
            authorization_block_reason(
                package,
                authorization,
                "APPLICATION_SUBMISSION",
            ),
        )

    def test_unknown_action_is_blocked(self):
        package = self._approved_package()
        authorization = self._authorization(package)

        authorization.authorize(
            application_submission=True,
            outreach=True,
        )

        self.assertFalse(
            can_execute_action(
                package,
                authorization,
                "DELETE_MY_CAREER",
            )
        )

        self.assertIn(
            "Unknown execution action",
            authorization_block_reason(
                package,
                authorization,
                "DELETE_MY_CAREER",
            ),
        )


if __name__ == "__main__":
    unittest.main()


class ExecutionAuthorizationPersistenceTest(unittest.TestCase):

    def test_persisted_authorization_cannot_cross_package_versions(self):
        import tempfile
        from pathlib import Path

        import app.execution_authorization_store as store

        package = load_existing_application_package("JOB-001")
        self.assertIsNotNone(package)

        package = copy.deepcopy(package)
        package.status = OpportunityStatus.APPROVED
        package.approved_by_human = True
        package.content_hash = calculate_content_hash(package)
        package.approved_content_hash = package.content_hash

        authorization = ExecutionAuthorization(
            job_id=package.job_id,
            company=package.company,
            title=package.title,
            package_version=package.package_version,
            approved_content_hash=package.content_hash,
        )

        authorization.authorize(
            application_submission=True
        )

        with tempfile.TemporaryDirectory() as tmp:
            store.EXECUTION_AUTHORIZATION_DIR = Path(tmp)

            store.save_execution_authorization(
                authorization
            )

            loaded_authorization = (
                store.load_execution_authorization(
                    package.job_id
                )
            )

            self.assertIsNotNone(
                loaded_authorization
            )

            changed_package = copy.deepcopy(package)
            changed_package.package_version += 1

            self.assertFalse(
                can_execute_action(
                    changed_package,
                    loaded_authorization,
                    "APPLICATION_SUBMISSION",
                )
            )

            self.assertIn(
                "version does not match",
                authorization_block_reason(
                    changed_package,
                    loaded_authorization,
                    "APPLICATION_SUBMISSION",
                ),
            )


if __name__ == "__main__":
    unittest.main()
