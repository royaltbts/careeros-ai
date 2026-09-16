from pathlib import Path

import unittest

from app.models.opportunity_decision_audit import (
    OpportunityDecisionAudit,
)
from app.opportunity_decision_audit_store import (
    load_opportunity_decision_audit,
    save_opportunity_decision_audit,
)


class OpportunityDecisionAuditStoreTest(unittest.TestCase):

    def test_audit_history_is_preserved(self):
        audit_file = Path(
            "data/jobs/opportunity_decision_audit/TEST-AUDIT-001.json"
        )
        audit_file.unlink(missing_ok=True)
        self.addCleanup(
            lambda: audit_file.unlink(missing_ok=True)
        )

        first = OpportunityDecisionAudit(
            job_id="TEST-AUDIT-001",
            company="Test Company",
            title="Customer Success Manager",
            opportunity_score=95.0,
            priority="HIGH",
            recommendation="APPLY",
        )

        second = OpportunityDecisionAudit(
            job_id="TEST-AUDIT-001",
            company="Test Company",
            title="Customer Success Manager",
            opportunity_score=70.0,
            priority="REVIEW",
            recommendation="REVIEW",
        )

        save_opportunity_decision_audit(first)
        save_opportunity_decision_audit(second)

        history = load_opportunity_decision_audit(
            "TEST-AUDIT-001"
        )

        self.assertEqual(len(history), 2)

        self.assertEqual(
            history[0].recommendation,
            "APPLY",
        )

        self.assertEqual(
            history[1].recommendation,
            "REVIEW",
        )

        self.assertEqual(
            history[0].opportunity_score,
            95.0,
        )

        self.assertEqual(
            history[1].opportunity_score,
            70.0,
        )


if __name__ == "__main__":
    unittest.main()
