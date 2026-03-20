from typing import List
from domain.types.candle import Candle
from services.trade_engine.interface import TradeEngine
from domain.models.trade_unit import Trade_unit
from domain.models.decision import Decision


class TradeEngineAdapter(TradeEngine):
    """Адаптер для работы с FSM-движками через интерфейс TradeEngine"""

    def __init__(self, trade_engine):
        self._engine = trade_engine

    def handle_first(self, trade_unit: Trade_unit) -> Decision:
        return self._engine.handle_first(trade_unit)

    def deposit(self) -> float:
        return self._engine.deposit()

    def window(self) -> List[Candle]:
        return self._engine.window()

    def get_cooldown(self) -> int:
        return self._engine.get_cooldown()

    def report_reset(self) -> None:
        return self._engine.report_reset()

    def engine_id(self) -> str:
        return self._engine.engine_id()
