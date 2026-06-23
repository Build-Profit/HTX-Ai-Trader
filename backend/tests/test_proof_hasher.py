import unittest

from app.services.proof_hasher import generate_proof, sha256_hex


class ProofHasherTest(unittest.TestCase):
    def test_hash_is_deterministic_for_key_order(self):
        left = {"b": 2, "a": 1}
        right = {"a": 1, "b": 2}

        self.assertEqual(sha256_hex(left), sha256_hex(right))

    def test_combined_hash_changes_when_strategy_changes(self):
        backtest = {"totalReturnPercent": 1.2}
        logs = [{"event": "order_created"}]

        first = generate_proof({"symbol": "BTC/USDT"}, backtest, logs)
        second = generate_proof({"symbol": "ETH/USDT"}, backtest, logs)

        self.assertNotEqual(first.combined_hash, second.combined_hash)


if __name__ == "__main__":
    unittest.main()
