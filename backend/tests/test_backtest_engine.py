import unittest

from app.services.backtest_engine import run_backtest
from app.services.htx_market import load_sample_klines
from app.services.strategy_parser import parse_strategy_text


class BacktestEngineTest(unittest.TestCase):
    def test_backtest_outputs_reproducible_metrics(self):
        strategy = parse_strategy_text("Use 1000 USDT on BTC/USDT. Buy when BTC drops 5%, take profit at 10%, stop loss at 3%, max drawdown 5%.")
        klines = load_sample_klines("BTC/USDT", "1h", 120)

        first = run_backtest(strategy, klines, data_source="local_sample")
        second = run_backtest(strategy, klines, data_source="local_sample")

        self.assertEqual(first.to_dict(), second.to_dict())
        self.assertGreaterEqual(first.trade_count, 1)
        self.assertNotEqual(first.total_return_percent, first.buy_hold_return_percent)
        self.assertGreater(len(first.equity_curve), 0)

    def test_backtest_parameter_changes_result(self):
        klines = load_sample_klines("BTC/USDT", "1h", 120)
        strategy_a = parse_strategy_text("Use 1000 USDT on BTC/USDT. Buy drop 5%, take profit 10%, stop loss 3%.")
        strategy_b = parse_strategy_text("Use 1000 USDT on BTC/USDT. Buy drop 7%, take profit 6%, stop loss 2%.")

        result_a = run_backtest(strategy_a, klines, data_source="local_sample")
        result_b = run_backtest(strategy_b, klines, data_source="local_sample")

        self.assertNotEqual(result_a.to_dict()["trades"], result_b.to_dict()["trades"])


if __name__ == "__main__":
    unittest.main()
