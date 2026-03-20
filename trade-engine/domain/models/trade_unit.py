from typing import NamedTuple

from domain.types.candle import Candle


class Trade_unit(NamedTuple):
    candle: Candle
    spread: float
    deposit: float
