from abc import ABC, abstractmethod
from typing import List, Tuple

from domain.types.candle import Candle


class WindowOperator(ABC):
    @abstractmethod
    def shift_window(self, candle: Candle): ...

    @abstractmethod
    def window_len(self) -> int: ...

    @abstractmethod
    def last_n_candles(self, n: int) -> List[Candle]: ...

    @abstractmethod
    def all_candles(self) -> List[Candle]: ...
