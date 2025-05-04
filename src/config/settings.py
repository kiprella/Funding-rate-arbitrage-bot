from typing import Dict
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BYBIT_API_KEY: str = os.getenv('BYBIT_API_KEY', '')
    BYBIT_API_SECRET: str = os.getenv('BYBIT_API_SECRET', '')
    BYBIT_TESTNET: bool = os.getenv('BYBIT_TESTNET', 'False').lower() == 'true'
    TRADING_PAIRS: list = ["BTCUSDT", "ETHUSDT"]

    @classmethod
    def get_bybit_config(cls) -> Dict[str, str]:
        return {
            "api_key": cls.BYBIT_API_KEY,
            "api_secret": cls.BYBIT_API_SECRET,
            "testnet": cls.BYBIT_TESTNET
        } 