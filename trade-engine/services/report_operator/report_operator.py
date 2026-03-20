from typing import List

from domain.models.order import Order
from domain.models.report import Report
from domain.types.candle import Candle
from services.report_operator.interface import ReportOperator


class ReportOperatorImpl(ReportOperator):
    def report(
        self, candles: List[Candle], order: Order, reason: str, profit: float
    ) -> Report:
        report = Report(candles=candles, order=order, reason=reason, profit=profit)

        return report
