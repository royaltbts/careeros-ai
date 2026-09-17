import unittest
from unittest.mock import patch

from app.job_discovery_greenhouse import GreenhouseJobDiscoveryProvider


class TestGreenhouseJobDiscoveryProvider(unittest.TestCase):

    @patch.object(GreenhouseJobDiscoveryProvider, "_get")
    def test_discovers_customer_success_roles_and_cleans_details(self, mock_get):
        mock_get.side_effect = [
            {
                "jobs": [
                    {
                        "id": 101,
                        "title": "Customer Success Manager",
                        "location": {"name": "Hyderabad, India"},
                        "absolute_url": "https://example.com/csm",
                    },
                    {
                        "id": 102,
                        "title": "Senior Software Engineer",
                        "location": {"name": "Hyderabad, India"},
                        "absolute_url": "https://example.com/engineer",
                    },
                ]
            },
            {
                "id": 101,
                "title": "Customer Success Manager",
                "company_name": "Example SaaS",
                "location": {"name": "Hyderabad, India"},
                "absolute_url": "https://example.com/csm",
                "content": """
                    <p>Own customer relationships.</p>
                    <p>This is a <strong>hybrid</strong> role.</p>
                """,
            },
        ]

        provider = GreenhouseJobDiscoveryProvider("example")
        results = provider.discover()

        self.assertEqual(len(results), 1)

        job = results[0]
        self.assertEqual(job.job_id, "GH-example-101")
        self.assertEqual(job.company, "Example SaaS")
        self.assertEqual(job.title, "Customer Success Manager")
        self.assertEqual(job.location, "Hyderabad, India")
        self.assertEqual(job.source, "Greenhouse")
        self.assertEqual(job.source_url, "https://example.com/csm")
        self.assertEqual(job.work_mode, "hybrid")

        self.assertNotIn("<p>", job.raw_description)
        self.assertNotIn("<strong>", job.raw_description)
        self.assertIn("Own customer relationships.", job.raw_description)

        self.assertEqual(mock_get.call_count, 2)


    @patch.object(GreenhouseJobDiscoveryProvider, "_get")
    def test_returns_empty_when_greenhouse_request_fails(self, mock_get):
        mock_get.return_value = None

        provider = GreenhouseJobDiscoveryProvider("example")
        results = provider.discover()

        self.assertEqual(results, [])
        mock_get.assert_called_once()

    def test_rejects_empty_board_token(self):
        provider = GreenhouseJobDiscoveryProvider("")

        with self.assertRaises(ValueError):
            provider.discover()


if __name__ == "__main__":
    unittest.main()
