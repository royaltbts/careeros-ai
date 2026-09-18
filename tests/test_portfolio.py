import unittest

from app.portfolio import build_portfolio


class PortfolioTest(unittest.TestCase):

    def test_portfolio_loads_canonical_candidate_data(self):
        portfolio = build_portfolio()

        self.assertEqual(
            portfolio["candidate"].career_direction["primary"],
            "Customer Success",
        )
        self.assertEqual(
            len(portfolio["evidence"]),
            8,
        )
        self.assertEqual(
            portfolio["career_strategy"].primary_direction,
            "Customer Success",
        )


if __name__ == "__main__":
    unittest.main()
