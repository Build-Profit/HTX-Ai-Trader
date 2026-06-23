import unittest

from app.services.htx_market import load_sample_klines
from app.services.simulator import simulate_trade
from app.services.strategy_parser import parse_strategy_text


class SimulatorTest(unittest.TestCase):
    def test_simulator_generates_order_lifecycle(self):
        strategy = parse_strategy_text("Use 1000 USDT on BTC/USDT. Buy drop 5%, take profit 10%, stop loss 3%.")
        klines = load_sample_klines("BTC/USDT", "1h", 30)

        logs = simulate_trade(strategy, klines)
        events = [item.event for item in logs]

        self.assertIn("order_created", events)
        self.assertIn("order_filled", events)
        self.assertIn(logs[-1].status, {"closed", "filled"})


if __name__ == "__main__":
    unittest.main()
