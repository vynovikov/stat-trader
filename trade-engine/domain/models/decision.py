from typing import NamedTuple

from domain.models.order import Order
from domain.models.report import Report
from domain.models.TPSL import TPSL
from domain.types.market_action import MarketAction


class Decision(NamedTuple):
    engine_id: str
    order: Order
    tpsl: TPSL
    action: MarketAction
    report: Report
