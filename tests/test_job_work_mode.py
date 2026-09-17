import unittest

from app.job_work_mode import detect_work_mode


class TestJobWorkMode(unittest.TestCase):

    def test_detects_remote(self):
        self.assertEqual(
            detect_work_mode("This is a fully remote position."),
            "remote",
        )

    def test_detects_remote_first(self):
        self.assertEqual(
            detect_work_mode("We are a remote-first organization."),
            "remote",
        )

    def test_detects_hybrid(self):
        self.assertEqual(
            detect_work_mode("This is a hybrid role with flexible scheduling."),
            "hybrid",
        )

    def test_detects_on_site(self):
        self.assertEqual(
            detect_work_mode("This is an on-site position."),
            "on-site",
        )

    def test_returns_none_when_unspecified(self):
        self.assertIsNone(
            detect_work_mode("Location details are provided during the interview."),
        )


if __name__ == "__main__":
    unittest.main()
