from abc import ABC, abstractmethod
from typing import Dict, Any

class ExchangeInterface(ABC):
    @abstractmethod
    async def connect(self) -> bool:"
        pass

    @abstractmethod
    async def get_funding_rate(self, symbol: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        pass 