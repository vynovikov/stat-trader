from typing import List

from domain.types.candle import Candle
from services.history_operator.interface import HistoryOperator


class HistoryOperatorImpl(HistoryOperator):
    def __init__(
        self,
    ) -> None:
        self.history_candles: List[Candle] = []

    def set(self, candles: List[Candle]) -> None:
        self.history_candles = candles

    def get(self) -> List[Candle]:
        return list(self.history_candles)

    def clear(self) -> None:
        self.history_candles = []

    def add(self, candle: Candle) -> None:
        candles = self.get()
        candles.append(candle)
        self.set(candles)
