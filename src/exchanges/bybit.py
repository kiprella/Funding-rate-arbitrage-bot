import aiohttp
from typing import Dict, Any, List
from .interface import ExchangeInterface

class BybitExchange(ExchangeInterface):
    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api-testnet.bybit.com" if testnet else "https://api.bybit.com"
        self.session = None

    async def connect(self) -> bool:
        """Establish connection to Bybit exchange"""
        try:
            self.session = aiohttp.ClientSession()
            return True
        except Exception as e:
            print(f"Failed to connect to Bybit: {str(e)}")
            return False

    async def get_perpetual_tickers(self) -> List[str]:
        """
        Get all available perpetual trading pairs from Bybit
        
        Returns:
            List[str]: List of perpetual trading pair symbols
        """
        if not self.session:
            raise ConnectionError("Not connected to Bybit. Call connect() first.")

        endpoint = "/v5/market/instruments-info"
        params = {
            "category": "linear"
        }

        try:
            async with self.session.get(f"{self.base_url}{endpoint}", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['retCode'] == 0:
                        # Extract symbols from the response
                        symbols = [item['symbol'] for item in data['result']['list']]
                        return symbols
                    else:
                        raise Exception(f"Failed to fetch tickers: {data['retMsg']}")
                else:
                    raise Exception(f"Failed to fetch tickers: {response.status}")
        except Exception as e:
            raise Exception(f"Error fetching tickers: {str(e)}")

    async def get_funding_rate(self, symbol: str) -> Dict[str, Any]:
        """
        Get funding rate for a specific symbol from Bybit
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            Dict[str, Any]: Funding rate information
        """
        if not self.session:
            raise ConnectionError("Not connected to Bybit. Call connect() first.")

        endpoint = f"/v5/market/funding/history"
        params = {
            "category": "linear",
            "symbol": symbol
        }

        try:
            async with self.session.get(f"{self.base_url}{endpoint}", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    raise Exception(f"Failed to fetch funding rate: {response.status}")
        except Exception as e:
            raise Exception(f"Error fetching funding rate: {str(e)}")

    async def disconnect(self) -> None:
        """Close connection to Bybit exchange"""
        if self.session:
            await self.session.close()
            self.session = None 