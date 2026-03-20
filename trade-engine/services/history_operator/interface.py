from abc import ABC, abstractmethod
from typing import List

from domain.types.candle import Candle


class HistoryOperator(ABC):
    @abstractmethod
    def set(self, candles: List[Candle]) -> None: ...

    @abstractmethod
    def add(self, candle: Candle) -> None: ...

    @abstractmethod
    def get(self) -> List[Candle]: ...

    @abstractmethod
    def clear(self) -> None: ...
