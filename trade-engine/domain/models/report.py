from typing import NamedTuple,List

from domain.models.order import Order
from domain.models.TPSL import TPSL
from domain.types.candle import Candle


class Report(NamedTuple):
    candles: List[Candle] = []
    orders: List[Order] = []
    tpsl: TPSL = TPSL()
    profit: float = 0.0
    reason: str = ""
