import asyncio
from typing import Optional
from src.exchanges.bybit import BybitExchange
from src.config.settings import Config

class TradingEngine:
    def __init__(self):
        self.exchange: Optional[BybitExchange] = None
        self.is_connected: bool = False

    async def initialize(self) -> bool:
        try:
            while True:
                env_choice = input("Select environment (1 for Production, 2 for Testnet): ").strip()
                if env_choice in ['1', '2']:
                    break
                print("Invalid choice. Please enter 1 for Production or 2 for Testnet.")

            Config.BYBIT_TESTNET = env_choice == '2'
            
            bybit_config = Config.get_bybit_config()
            
            self.exchange = BybitExchange(
                api_key=bybit_config["api_key"],
                api_secret=bybit_config["api_secret"],
                testnet=bybit_config["testnet"]
            )

            self.is_connected = await self.exchange.connect()
            
            if self.is_connected:
                env_type = "Testnet" if Config.BYBIT_TESTNET else "Production"
                print(f"Successfully connected to Bybit {env_type}")
                return True
            else:
                print("Failed to connect to Bybit")
                return False

        except Exception as e:
            print(f"Error initializing engine: {str(e)}")
            return False

    async def get_funding_rate(self, symbol: str) -> dict:
        if not self.is_connected or not self.exchange:
            raise ConnectionError("Engine not initialized or not connected")
        
        try:
            return await self.exchange.get_funding_rate(symbol)
        except Exception as e:
            print(f"Error getting funding rate: {str(e)}")
            raise

    async def shutdown(self):
        if self.exchange:
            await self.exchange.disconnect()
            self.is_connected = False
            print("Trading engine shutdown complete") 