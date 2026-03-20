from abc import ABC, abstractmethod
from typing import List

from domain.models.trade_unit import Trade_unit
from domain.models.decision import Decision
from domain.types.candle import Candle


class Usecases(ABC):
    @abstractmethod
    def decide(
        self,
        trade_unit: Trade_unit,
    ) -> Decision: ...
