from abc import ABC, abstractmethod
from typing import Dict, Any

class ExchangeInterface(ABC):
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to the exchange"""
        pass

    @abstractmethod
    async def get_funding_rate(self, symbol: str) -> Dict[str, Any]:
        """Get funding rate for a specific symbol"""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the exchange"""
        pass 