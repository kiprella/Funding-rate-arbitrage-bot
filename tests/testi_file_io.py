import unittest
from unittest.mock import patch, mock_open
from tickers_info.fetch_tickers import save_tickers_to_csv
import os

class TestFileIO(unittest.IsolatedAsyncioTestCase):
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.makedirs")
    @patch("os.path.exists", return_value=False)
    async def test_save_tickers_to_csv(self, mock_exists, mock_makedirs, mock_file):
        tickers = ["BTCUSDT", "ETHUSDT"]
        exchange = "bybit"
        await save_tickers_to_csv(tickers, exchange)
        # Check that file was opened and written to
        self.assertTrue(mock_file.called)
        handle = mock_file()
        # Check that header and tickers were written
        written = "".join(call.args[0] for call in handle.write.call_args_list)
        self.assertIn("Exchange,Symbol,Timestamp", written)
        self.assertIn("bybit,BTCUSDT", written)
        self.assertIn("bybit,ETHUSDT", written)

if __name__ == "__main__":
    unittest.main()
