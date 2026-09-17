import json
import tempfile
import unittest
from pathlib import Path

from app.job_discovery_local import LocalJobDiscoveryProvider


class TestLocalJobDiscoveryProvider(unittest.TestCase):

    def test_loads_and_validates_jobs_from_json(self):
        jobs = [
            {
                "job_id": "LOCAL-001",
                "company": "Example",
                "title": "Customer Success Manager",
                "location": "Hyderabad, India",
                "work_mode": "hybrid",
                "source": "Local",
                "source_url": "https://example.com/job",
                "discovered_at": "2026-09-16",
                "raw_description": "Customer Success role.",
            }
        ]

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "jobs.json"
            path.write_text(json.dumps(jobs), encoding="utf-8")

            provider = LocalJobDiscoveryProvider(str(path))
            results = provider.discover()

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].job_id, "LOCAL-001")
        self.assertEqual(results[0].title, "Customer Success Manager")
        self.assertEqual(results[0].work_mode, "hybrid")

    def test_rejects_invalid_job_record(self):
        jobs = [
            {
                "job_id": "LOCAL-002",
                "company": "Example",
                "title": "Customer Success Manager",
            }
        ]

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "jobs.json"
            path.write_text(json.dumps(jobs), encoding="utf-8")

            provider = LocalJobDiscoveryProvider(str(path))

            with self.assertRaises(Exception):
                provider.discover()


if __name__ == "__main__":
    unittest.main()
