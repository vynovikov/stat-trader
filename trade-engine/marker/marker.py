from dataclasses import dataclass
from typing import List, Optional, Tuple

import pandas as pd

from domain.models.segment import Segment
from domain.models.trade_params import TradeParams
from domain.types.candle import Candle
from domain.types.direction import Direction
from services.estimator.interface import Estimator
from utils.candle_utils import candle_from_series


@dataclass
class Marker:

    estimator: Estimator
    a_len: int = 4  # Number of candles in Pre

    def mark(self, df: pd.DataFrame) -> List[Segment]:
        if len(df) < self.a_len + 6:  # Not enough data to form a segment
            return []

        segments: List[Segment] = []
        i = self.a_len

        direction, trend, pre = self.new_vars()

        while i < len(df):
            c0 = self.idx_to_candle(i, df)
            c1 = self.idx_to_candle(i + 1, df) if i + 1 < len(df) else None

            match direction:
                case Direction.UNKNOWN:
                    if self.is_uptrend_started(c0, c1):
                        direction = Direction.UP

                        for idx in range(i - self.a_len, i):
                            pre.append(self.idx_to_candle(idx, df))

                        trend.append(c0)
                    elif self.is_downtrend_started(c0, c1):
                        direction = Direction.DOWN

                        for idx in range(i - self.a_len, i):
                            pre.append(self.idx_to_candle(idx, df))

                        trend.append(c0)

                case Direction.UP:
                    trend.append(c0)

                    if self.is_uptrend_continues(c0) == False:  # Trend ended
                        estimation = self.estimator.estimate(
                            candles=trend, direction=direction, from_candle_id=2
                        )

                        segments.append(
                            Segment(
                                Pre=pre.copy(),
                                Trend=trend.copy(),
                                Params=TradeParams(
                                    direction=direction,
                                    category=estimation.category,
                                    profit=round(estimation.profit, 2),
                                    risk=round(estimation.risk, 2),
                                    profit_risk_ratio=round(
                                        estimation.profit_risk_ratio, 2
                                    ),
                                    candles_num=self.estimator.candles_num(
                                        candles=trend
                                    ),
                                ),
                            )
                        )

                        direction, trend, pre = self.new_vars()

                case Direction.DOWN:
                    trend.append(c0)
                    if self.is_downtrend_continues(c0) == False:  # Trend ended
                        estimation = self.estimator.estimate(
                            candles=trend, direction=direction, from_candle_id=2
                        )

                        segments.append(
                            Segment(
                                Pre=pre.copy(),
                                Trend=trend.copy(),
                                Params=TradeParams(
                                    direction=direction,
                                    category=estimation.category,
                                    profit=round(estimation.profit, 2),
                                    risk=round(estimation.risk, 2),
                                    profit_risk_ratio=round(
                                        estimation.profit_risk_ratio, 2
                                    ),
                                    candles_num=self.estimator.candles_num(
                                        candles=trend
                                    ),
                                ),
                            )
                        )

                        direction, trend, pre = self.new_vars()

            i += 1

        return segments

    def idx_to_candle(self, idx: int, df: pd.DataFrame) -> Candle:
        row = df.iloc[idx]

        candle = candle_from_series(row)

        return candle

    def add_a_to_segment(self, df: pd.DataFrame, segment: Segment, idx: int):
        """Add prelude candles to segment - clean version without MA logic"""
        if idx < self.a_len:
            return

        # Simply add candles to prelude
        for i in range(idx - self.a_len, idx):
            segment.add_to_pre(self.idx_to_candle(i, df))

    def is_uptrend_started(
        self,
        c0: Candle,
        c1: Optional[Candle],
    ) -> bool:
        return (
            c1 is not None
            and c0.close > c0.open
            and c1.close > c1.open
            and c1.high > c0.high
        )

    def is_downtrend_started(
        self,
        c0: Candle,
        c1: Optional[Candle],
    ) -> bool:
        return (
            c1 is not None
            and c0.close < c0.open
            and c1.close < c1.open
            and c1.low < c0.low
        )

    def is_uptrend_continues(
        self,
        c0: Candle,
    ) -> bool:
        return c0.close > c0.open

    def is_downtrend_continues(
        self,
        c0: Candle,
    ) -> bool:
        return c0.close < c0.open

    def new_vars(self) -> Tuple[Direction, List[Candle], List[Candle]]:
        return Direction.UNKNOWN, [], []
