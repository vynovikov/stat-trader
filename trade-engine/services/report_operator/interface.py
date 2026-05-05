from abc import ABC, abstractmethod
from typing import List

from domain.models.order import Order
from domain.models.report import Report
from domain.models.TPSL import TPSL
from domain.types.candle import Candle


class ReportOperator(ABC):
    @abstractmethod
    def report(
        self,
        candles: List[Candle],
        orders: List[Order],
        tpsl: TPSL,
        reason: str,
        profit: float
    ) -> Report: ...
