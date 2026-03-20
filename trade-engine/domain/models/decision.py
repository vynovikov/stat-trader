from typing import NamedTuple

from domain.models.order import Order
from domain.models.report import Report
from domain.types.market_action import MarketAction


class Decision(NamedTuple):
    engine_id: str
    order: Order
    action: MarketAction
    report: Report
