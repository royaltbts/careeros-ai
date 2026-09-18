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

    def test_extracts_unsectioned_customer_success_description(self):
        job = JobDiscovery(
            job_id="TEST-CS-002",
            company="CustomerFirst SaaS",
            title="Customer Success Manager",
            location="Remote",
            work_mode="remote",
            source="TEST",
            source_url="https://example.com/jobs/TEST-CS-002",
            discovered_at="2026-09-17T00:00:00Z",
            raw_description=(
                "We are looking for a Customer Success Manager to build strong "
                "customer relationships, conduct regular business reviews, "
                "monitor customer satisfaction, manage escalations, coordinate "
                "with internal teams and improve customer outcomes. "
                "5+ years of customer-facing experience. "
                "Experience leading teams and driving continuous improvement "
                "is valued."
            ),
        )

        intelligence = build_job_intelligence(job)

        self.assertGreater(
            len(intelligence.responsibilities),
            0
        )
        self.assertIn(
            "build strong customer relationships",
            intelligence.responsibilities
        )
        self.assertGreater(
            len(intelligence.requirements),
            0
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
            "Customer relationship management",
            requirement_names
        )
        self.assertIn(
            "Customer satisfaction",
            requirement_names
        )
        self.assertIn(
            "Escalation management",
            requirement_names
        )
        self.assertIn(
            "Continuous improvement",
            requirement_names
        )

    def test_extracts_strategic_customer_success_description(self):
        job = JobDiscovery(
            job_id="TEST-CS-003",
            company="EnterpriseCloud",
            title="Strategic Customer Success Manager",
            location="Remote",
            work_mode="remote",
            source="TEST",
            source_url="https://example.com/jobs/TEST-CS-003",
            discovered_at="2026-09-17T00:00:00Z",
            raw_description=(
                "The Strategic Customer Success Manager will manage relationships "
                "with strategic customers, conduct executive business reviews, "
                "drive adoption, monitor customer health, manage escalations and "
                "coordinate cross-functional teams. Experience with enterprise "
                "SaaS customers and customer success platforms is preferred."
            ),
        )

        intelligence = build_job_intelligence(job)

        self.assertIn(
            "manage relationships with strategic customers",
            intelligence.responsibilities
        )
        self.assertIn(
            "conduct executive business reviews",
            intelligence.responsibilities
        )
        self.assertIn(
            "monitor customer health",
            intelligence.responsibilities
        )

        requirement_names = {
            requirement.name
            for requirement in intelligence.requirements
        }

        self.assertIn(
            "Customer health",
            requirement_names
        )
        self.assertIn(
            "SaaS experience",
            requirement_names
        )
        self.assertIn(
            "Customer Success platform experience",
            requirement_names
        )


if __name__ == "__main__":
    unittest.main()
