import unittest

from app.services.strategy_parser import parse_strategy_text


class StrategyParserTest(unittest.TestCase):
    def test_parse_chinese_strategy(self):
        strategy = parse_strategy_text("用 1000 USDT 做 BTC/USDT 低风险策略，跌5%买入，涨10%止盈，最大亏损3%，最大回撤不超过5%")

        self.assertEqual(strategy.symbol, "BTC/USDT")
        self.assertEqual(strategy.capital, 1000)
        self.assertEqual(strategy.entry.drop_percent, 5)
        self.assertEqual(strategy.exit.take_profit_percent, 10)
        self.assertEqual(strategy.exit.stop_loss_percent, 3)
        self.assertEqual(strategy.risk.max_drawdown_percent, 5)
        self.assertEqual(strategy.risk.risk_level, "low")

    def test_parse_english_strategy(self):
        strategy = parse_strategy_text("Use 2500 USDT on ETH/USDT 1h. Buy after drop 4%, take profit 8%, stop loss 2%, position 25%.")

        self.assertEqual(strategy.symbol, "ETH/USDT")
        self.assertEqual(strategy.timeframe, "1h")
        self.assertEqual(strategy.capital, 2500)
        self.assertEqual(strategy.entry.drop_percent, 4)
        self.assertEqual(strategy.exit.take_profit_percent, 8)
        self.assertEqual(strategy.exit.stop_loss_percent, 2)
        self.assertEqual(strategy.risk.position_size_percent, 25)


if __name__ == "__main__":
    unittest.main()
