# tests/test_bybit_exchange.py

import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from src.exchanges.bybit import BybitExchange

class TestBybitExchange(unittest.IsolatedAsyncioTestCase):
    @patch("aiohttp.ClientSession")
    async def test_connect(self, mock_session):
        exchange = BybitExchange("key", "secret", testnet=True)
        result = await exchange.connect()
        self.assertTrue(result)
        self.assertIsNotNone(exchange.session)

    @patch("aiohttp.ClientSession.get")
    async def test_get_perpetual_tickers(self, mock_get):
        # Mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "retCode": 0,
            "result": {"list": [{"symbol": "BTCUSDT"}, {"symbol": "ETHUSDT"}]}
        }
        mock_get.return_value.__aenter__.return_value = mock_response

        exchange = BybitExchange("key", "secret", testnet=True)
        exchange.session = MagicMock()
        exchange.session.get = mock_get

        tickers = await exchange.get_perpetual_tickers()
        self.assertEqual(tickers, ["BTCUSDT", "ETHUSDT"])

    @patch("aiohttp.ClientSession.get")
    async def test_get_funding_rate(self, mock_get):
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "retCode": 0,
            "result": {"list": [{"fundingRate": "0.0001", "fundingRateTimestamp": "1710000000000"}]}
        }
        mock_get.return_value.__aenter__.return_value = mock_response

        exchange = BybitExchange("key", "secret", testnet=True)
        exchange.session = MagicMock()
        exchange.session.get = mock_get

        data = await exchange.get_funding_rate("BTCUSDT")
        self.assertIn("retCode", data)
        self.assertEqual(data["retCode"], 0)

if __name__ == "__main__":
    unittest.main()