from abc import ABC, abstractmethod
from typing import List

from domain.models.segment import Segment
from domain.types.candle import Candle
from domain.types.category import Category


class VectorOperator(ABC):
    @abstractmethod
    def segment(
        self, candles: List[Candle], category: Category, risk: float, vector_ttl: int
    ) -> Segment: ...
