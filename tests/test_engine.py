import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from src.engine.trading_engine import TradingEngine

class TestTradingEngine(unittest.IsolatedAsyncioTestCase):
    @patch("src.engine.trading_engine.input", return_value="1")
    @patch("src.engine.trading_engine.BybitExchange")
    async def test_initialize_production(self, mock_bybit, mock_input):
        mock_exchange = AsyncMock()
        mock_exchange.connect.return_value = True
        mock_bybit.return_value = mock_exchange

        engine = TradingEngine()
        result = await engine.initialize()
        self.assertTrue(result)
        self.assertIsNotNone(engine.exchange)
        self.assertTrue(engine.is_connected)

    @patch("src.engine.trading_engine.input", return_value="2")
    @patch("src.engine.trading_engine.BybitExchange")
    async def test_initialize_testnet(self, mock_bybit, mock_input):
        mock_exchange = AsyncMock()
        mock_exchange.connect.return_value = True
        mock_bybit.return_value = mock_exchange

        engine = TradingEngine()
        result = await engine.initialize()
        self.assertTrue(result)
        self.assertIsNotNone(engine.exchange)
        self.assertTrue(engine.is_connected)

if __name__ == "__main__":
    unittest.main()
