from typing import NamedTuple

from domain.models.order import Order
from domain.types.candle import Candle


class Report(NamedTuple):
    candles: list[Candle] = []
    order: Order = Order()
    profit: float = 0.0
    reason: str = ""
