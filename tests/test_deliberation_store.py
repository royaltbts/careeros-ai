import unittest
from uuid import uuid4

from app.deliberation_store import (
    load_deliberations,
    save_deliberation,
)
from app.models.deliberation_record import (
    DeliberationRecord,
)


class DeliberationStoreTest(unittest.TestCase):

    def test_save_and_load_deliberation(self):
        job_id = f"TEST-DELIBERATION-{uuid4().hex}"

        record = DeliberationRecord(
            job_id=job_id,
            company="Example SaaS",
            title="Customer Success Manager",
            cycle_id="cycle-001",
            agent_findings=[
                {
                    "agent": "Risk Agent",
                    "recommendation": "REVIEW",
                }
            ],
            disagreements=[
                {
                    "agents": [
                        "Candidate Fit Agent",
                        "Risk Agent",
                    ],
                    "topic": (
                        "Formal SaaS/CRM/"
                        "account-ownership experience"
                    ),
                    "positions": [
                        "Candidate Fit Agent: APPLY",
                        "Risk Agent: REVIEW",
                    ],
                    "resolution_required": True,
                }
            ],
            supervisor_recommendation="APPLY",
            supervisor_confidence=0.90,
            supervisor_conflicts=[
                "Non-blocking risk requires human review."
            ],
            unresolved_questions=[
                "Should the experience gap materially affect the opportunity?"
            ],
            human_review_required=True,
            external_action_allowed=False,
        )

        save_supervisor_path = save_deliberation(record)
        self.assertTrue(
            save_supervisor_path.exists()
        )

        records = load_deliberations(job_id)

        self.assertEqual(
            len(records),
            1,
        )

        loaded = records[0]

        self.assertEqual(
            loaded.job_id,
            job_id,
        )
        self.assertEqual(
            loaded.supervisor_recommendation,
            "APPLY",
        )
        self.assertEqual(
            loaded.supervisor_confidence,
            0.90,
        )
        self.assertTrue(
            loaded.human_review_required
        )
        self.assertFalse(
            loaded.external_action_allowed
        )
        self.assertEqual(
            len(loaded.agent_findings),
            1,
        )
        self.assertEqual(
            len(loaded.disagreements),
            1,
        )

    def test_deliberation_history_is_append_only(self):
        job_id = f"TEST-DELIBERATION-{uuid4().hex}"

        first = DeliberationRecord(
            job_id=job_id,
            company="Example SaaS",
            title="Customer Success Manager",
            cycle_id="cycle-001",
            supervisor_recommendation="REVIEW",
            supervisor_confidence=0.70,
        )

        second = DeliberationRecord(
            job_id=job_id,
            company="Example SaaS",
            title="Customer Success Manager",
            cycle_id="cycle-002",
            supervisor_recommendation="APPLY",
            supervisor_confidence=0.90,
        )

        save_deliberation(first)
        save_deliberation(second)

        records = load_deliberations(job_id)

        self.assertEqual(
            len(records),
            2,
        )

        self.assertEqual(
            records[0].cycle_id,
            "cycle-001",
        )
        self.assertEqual(
            records[1].cycle_id,
            "cycle-002",
        )
        self.assertEqual(
            records[0].supervisor_recommendation,
            "REVIEW",
        )
        self.assertEqual(
            records[1].supervisor_recommendation,
            "APPLY",
        )


if __name__ == "__main__":
    unittest.main()
