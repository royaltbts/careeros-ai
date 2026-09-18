import unittest

from app.market_scout_pipeline import build_job_intelligence
from app.models.job_discovery import JobDiscovery


class TestMarketScout(unittest.TestCase):

    def test_extracts_customer_success_job_intelligence(self):
        job = JobDiscovery(
            job_id="TEST-CS-001",
            company="Example SaaS",
            title="Customer Success Manager",
            location="Hyderabad",
            work_mode="hybrid",
            source="TEST",
            source_url="https://example.com/job",
            discovered_at="2026-09-17T00:00:00Z",
            raw_description="""
            Customer Success Manager

            Responsibilities:
            Own customer relationships and account plans.
            Drive customer adoption and satisfaction.
            Conduct business reviews with customers.
            Manage escalations and complex customer situations.
            Partner with internal stakeholders to solve customer problems.

            Requirements:
            5+ years of customer-facing experience.
            Experience managing customer relationships.
            Strong stakeholder management and communication skills.
            Experience hiring, training, and coaching customer-facing teams.
            Experience with SaaS products.
            Experience using CRM platforms.
            """
        )

        intelligence = build_job_intelligence(job)

        self.assertEqual(
            intelligence.job_id,
            "TEST-CS-001"
        )

        self.assertGreater(
            len(intelligence.requirements),
            0
        )

        self.assertGreater(
            len(intelligence.customer_success_capabilities),
            0
        )

        self.assertGreater(
            len(intelligence.responsibilities),
            0
        )

        self.assertIn(
            "Own customer relationships and account plans.",
            intelligence.responsibilities
        )

        self.assertIn(
            "Manage escalations and complex customer situations.",
            intelligence.responsibilities
        )

        self.assertEqual(
            intelligence.experience_required,
            "5+ years of customer-facing experience"
        )

        requirement_names = {
            requirement.name
            for requirement in intelligence.requirements
        }

        self.assertIn(
            "People leadership",
            requirement_names
        )

        self.assertIn(
            "Stakeholder management",
            requirement_names
        )

        self.assertIn(
            "SaaS experience",
            requirement_names
        )


if __name__ == "__main__":
    unittest.main()
