from datetime import datetime
from typing import NamedTuple

from domain.types.candle_action import CandleAction


class Order(NamedTuple):
    action: CandleAction = CandleAction.NONE
    time: datetime = datetime.min
    entry: float = 0.0
    sl: float = 0.0
    tp: float = 0.0
    volume: float = 0.0
