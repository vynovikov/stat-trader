from enum import Enum


class MarketAction(Enum):
    HOLD = "hold"
    OPEN = "open"
    CLOSE = "close"
    CLOSE_THEN_OPEN = "close_then_open"
