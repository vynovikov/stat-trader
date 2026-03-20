import os
import sys

# Получаем путь к текущему скрипту
current_dir = os.path.dirname(os.path.abspath(__file__))

# Поднимаемся на два уровня выше, чтобы попасть в корневой каталог проекта (ml-agent)
# Путь может быть другим, в зависимости от того, где находится config.py
project_root = os.path.abspath(os.path.join(current_dir, "../../"))

# Добавляем корневой каталог в sys.path
if project_root not in sys.path:
    sys.path.insert(0, project_root)


from typing import List

from domain.models.estimation import Estimation
from domain.types.candle import Candle
from domain.types.category import Category
from domain.types.direction import Direction
from services.estimator.interface import Estimator


class ReversalEstimator(Estimator):

    def __init__(self, min_trend_candles: int = 2) -> None:
        self.min_trend_candles = min_trend_candles
        self.candles_number = 1

    def estimate(
        self, candles: List[Candle], direction: Direction, from_candle_id: int
    ) -> Estimation:

        if len(candles) <= from_candle_id:
            return Estimation(
                category=Category.NONE,
                profit=0.0,
                risk=0.0,
                profit_risk_ratio=0.0,
            )

        category, profit, loss, profit_loss_ratio = Category.WISHFUL, 0.0, 0.0, 0.0
        reversal_candle = candles[from_candle_id]

        match direction:
            case Direction.UP:
                profit = reversal_candle.open - reversal_candle.close
                loss = reversal_candle.high - reversal_candle.open
                profit_loss_ratio = profit * 100 / loss if loss != 0 else 500

                if profit > 0:
                    category = Category.BEAR

            case Direction.DOWN:
                profit = reversal_candle.close - reversal_candle.open
                loss = reversal_candle.open - reversal_candle.low
                profit_loss_ratio = profit * 100 / loss if loss != 0 else 500

                if profit > 0:
                    category = Category.BULL

        return Estimation(
            category=category,
            profit=profit,
            risk=loss,
            profit_risk_ratio=profit_loss_ratio,
        )

    def candles_num(self, candles: List[Candle]) -> int:
        return 1
