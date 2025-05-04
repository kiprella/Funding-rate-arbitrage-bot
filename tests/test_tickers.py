import unittest
from tickers_info.fetch_tickers import filter_perpetual_pairs

class TestTickerFiltering(unittest.TestCase):
    def test_filter_perpetual_pairs(self):
        tickers = [
            "BTCUSDT", "ETHUSDT", "BTC-PERP", "ETHUSDC", "XRPUSDT", "BTCUSDT0329", "DOGEUSDT"
        ]
        expected = ["BTCUSDT", "ETHUSDT", "XRPUSDT", "DOGEUSDT"]
        result = filter_perpetual_pairs(tickers)
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()
