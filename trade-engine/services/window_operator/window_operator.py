from collections import deque
from typing import List

from domain.types.candle import Candle
from services.window_operator.interface import WindowOperator


class WindowOperatorImpl(WindowOperator):
    def __init__(
        self,
        maxlen_window: int = 11,
    ) -> None:
        if maxlen_window < 3:
            raise ValueError(f"maxlen_window must be >= 3, got {maxlen_window}")

        self.window = deque(maxlen=maxlen_window)
        self.trend: List[Candle] = []
        self.pre: List[Candle] = []

        self.maxlen_window = maxlen_window

    def shift_window(self, candle: Candle):
        self.window.append(candle)

    def window_len(self) -> int:
        return len(self.window)

    def last_n_candles(self, n: int) -> List[Candle]:
        if n <= 0:
            return []

        if n > self.window_len():
            n = self.window_len()

        candles = list(self.window)[-n:]

        return candles

    def all_candles(self) -> List[Candle]:
        return list(self.window)
