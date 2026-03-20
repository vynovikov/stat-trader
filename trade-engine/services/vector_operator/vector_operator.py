from datetime import timedelta
from typing import List

from domain.models.segment import Segment
from domain.models.trade_params import TradeParams
from domain.types.candle import Candle
from domain.types.category import Category
from services.vector_operator.interface import VectorOperator


class VectorOperatorImpl(VectorOperator):
    def segment(
        self, candles: List[Candle], category: Category, risk: float, vector_ttl: int
    ) -> Segment:
        created_at = candles[0].close_time
        expire_at = candles[0].close_time + timedelta(days=vector_ttl)
        segment = Segment(
            Pre=candles,
            Params=TradeParams(
                category=category, risk=risk, created_at=created_at, expire_at=expire_at
            ),
        )
        segment.update_pattern_characteristics(
            candles_limit=len(candles),
            ma_50s=[candle.ma_50 for candle in candles],
            ma_200s=[candle.ma_200 for candle in candles],
        )

        return segment
