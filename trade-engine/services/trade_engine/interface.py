from typing import List
from abc import ABC, abstractmethod

from domain.models.decision import Decision
from domain.models.trade_unit import Trade_unit
from domain.types.candle import Candle


class TradeEngine(ABC):
    @abstractmethod
    def handle_first(self, trade_unit: Trade_unit) -> Decision: ...

    @abstractmethod
    def deposit(self) -> float: ...

    @abstractmethod
    def window(self) -> List[Candle]: ...

    @abstractmethod
    def get_cooldown(self) -> int: ...

    @abstractmethod
    def report_reset(self) -> None: ...

    @abstractmethod
    def engine_id(self) -> str: ...
