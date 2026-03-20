from typing import List

from domain.models.estimation import Estimation
from domain.types.candle import Candle
from domain.types.category import Category
from domain.types.direction import Direction
from services.estimator.interface import Estimator


class ContinualEstimator(Estimator):
    """
    Estimator for trend continuation patterns.
    TODO: Implement logic for identifying and estimating continuation patterns.
    """

    def estimate(
        self, candles: List[Candle], direction: Direction, from_candle_id: int
    ) -> Estimation:
        """
        Placeholder implementation.
        Returns FLAT_REV estimation until proper logic is implemented.
        """
        # TODO: Implement actual continuation pattern estimation logic
        return Estimation(
            category=Category.NONE,
            profit=0.0,
            risk=0.0,
            profit_risk_ratio=0.0,
        )
