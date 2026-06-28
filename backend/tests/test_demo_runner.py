import unittest

from app.services.demo_runner import run_demo


class DemoRunnerTest(unittest.TestCase):
    def test_demo_runner_returns_full_loop(self):
        result = run_demo("Use 1000 USDT on BTC/USDT. Buy drop 5%, take profit 10%, stop loss 3%, max drawdown 5%.")

        self.assertIn("strategy", result)
        self.assertIn("backtest", result)
        self.assertIn("risk", result)
        self.assertIn("executionLogs", result)
        self.assertIn("proof", result)
        self.assertIn(result["market"]["source"], {"local_sample", "htx_cached", "htx_live"})


if __name__ == "__main__":
    unittest.main()
