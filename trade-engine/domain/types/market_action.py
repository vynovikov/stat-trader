from enum import Enum


class MarketAction(Enum):
    HOLD = "hold"
    OPEN = "open"
    ORDER_CREATE_TPSL_SET = "order_create_tpsl_set"
    ORDER_CREATE_TPSL_RESET = "order_create_tpsl_reset"
    CLOSE = "close"
    CLOSE_THEN_OPEN = "close_then_open"
