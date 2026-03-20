from abc import ABC, abstractmethod
from typing import List

from domain.models.order import Order
from domain.models.report import Report
from domain.types.candle import Candle


class ReportOperator(ABC):
    @abstractmethod
    def report(
        self, candles: List[Candle], order: Order, reason: str, profit: float
    ) -> Report: ...
