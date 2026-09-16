import os
import unittest
from unittest.mock import patch

from app.job_discovery_factory import discover_jobs
from app.models.career_strategy import CareerStrategy
from app.models.job_discovery import JobDiscovery


def strategy():
    return CareerStrategy(
        primary_direction="Customer Success",
        target_roles=["Customer Success Manager"],
        preferred_seniority=["Manager", "Senior Manager"],
        geography="Any",
        priority_capabilities=["Customer Success"],
        avoid_roles=[],
        strategy_notes=[],
    )


class TestJobDiscoveryFactory(unittest.TestCase):

    @patch("app.job_discovery_factory.GreenhouseJobDiscoveryProvider")
    def test_greenhouse_provider_is_selected_and_filtered(
        self,
        mock_provider_class,
    ):
        mock_provider = mock_provider_class.return_value
        mock_provider.discover.return_value = [
            JobDiscovery(
                job_id="JOB-LOCAL",
                company="Example",
                title="Customer Success Manager",
                location="Hyderabad, India",
                work_mode="hybrid",
                source="Greenhouse",
                source_url="https://example.com/local",
                discovered_at="2026-09-16",
                raw_description="CSM role",
            ),
            JobDiscovery(
                job_id="JOB-OFFSITE",
                company="Example",
                title="Customer Success Manager",
                location="London, UK",
                work_mode="on-site",
                source="Greenhouse",
                source_url="https://example.com/offsite",
                discovered_at="2026-09-16",
                raw_description="CSM role",
            ),
        ]

        with patch.dict(
            os.environ,
            {
                "CAREEROS_DISCOVERY_PROVIDER": "greenhouse",
                "CAREEROS_GREENHOUSE_BOARDS": "example",
            },
            clear=False,
        ):
            jobs, provider_name = discover_jobs(
                "unused.json",
                strategy=strategy(),
            )

        self.assertEqual(provider_name, "GREENHOUSE")
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].job_id, "JOB-LOCAL")
        mock_provider_class.assert_called_once_with("example")

    def test_greenhouse_requires_board_tokens(self):
        with patch.dict(
            os.environ,
            {
                "CAREEROS_DISCOVERY_PROVIDER": "greenhouse",
                "CAREEROS_GREENHOUSE_BOARDS": "",
            },
            clear=False,
        ):
            with self.assertRaises(ValueError):
                discover_jobs("unused.json", strategy=strategy())


if __name__ == "__main__":
    unittest.main()
