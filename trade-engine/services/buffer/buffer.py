from typing import Dict

import pandas as pd

from domain.types.candle import Candle
from utils.candle_utils import candle_from_series


class Buffer:
    """
    Two-channel buffer for synchronized iteration over low- and high-timeframe candles.

    Invariant:
        - Each index points to the *next* unread element for its timeframe.
        - After reading a high-TF candle, low_index is updated to the last low candle
          that belongs to the same period.
        - After reading a low-TF candle, high_index is updated to the next high candle
          once a full hl_ratio block of low candles is closed.

    Example:
        hl_ratio = 5  # (m5 vs m1)
        After reading high[0], low_index = 4
        After reading low[4], high_index = 1
    """

    def __init__(
        self,
        low_df: pd.DataFrame,
        high_df: pd.DataFrame,
        low_index: int = 0,
        high_index: int = 0,
        hl_ratio: int = 5,
    ):
        self.low_index: int = low_index
        self.high_index: int = high_index
        self.hl_ratio: int = hl_ratio
        self.tf: str = "high"

        self.store: Dict[str, pd.DataFrame] = dict(
            [
                ("low", low_df),
                ("high", high_df),
            ]
        )

    def set_tf(self, tf: str):
        """Switch active timeframe: either 'low' or 'high'."""

        self.tf = tf

    def get_candle(self) -> Candle:
        """
        Fetch the next unread candle from the active timeframe,
        update indices accordingly, and return as Candle object.
        """

        series: pd.Series

        match self.tf:
            case "high":
                if self.high_index >= len(self.store[self.tf]):
                    raise IndexError(
                        f"high_index {self.high_index} out of range for {len(self.store[self.tf])} rows"
                    )
                series = self.store[self.tf].iloc[self.high_index]
                self._update_indices_after_high()
            case "low":
                if self.low_index >= len(self.store[self.tf]):
                    raise IndexError(
                        f"low_index {self.low_index} out of range for {len(self.store[self.tf])} rows"
                    )
                series = self.store[self.tf].iloc[self.low_index]
                self._update_indices_after_low()

        candle = candle_from_series(series)

        return candle

    def _update_indices_after_high(self):
        """Advance high_index and sync low_index."""

        self.high_index += 1
        self.low_index = self._calc_low_index_after_high(self.high_index)

    def _update_indices_after_low(self):
        """Advance low_index and sync high_index."""

        self.low_index += 1
        self.high_index = self._calc_high_index_after_low(self.low_index)

    def _calc_low_index_after_high(self, next_high: int) -> int:
        """Compute low_index corresponding to the last low of the just-read high candle."""

        return next_high * self.hl_ratio - 1

    def _calc_high_index_after_low(self, next_low: int) -> int:
        """
        Compute the next high_index after reading one low candle.
        This jumps to the next high candle once a block of hl_ratio lows is closed.
        """

        return next_low // self.hl_ratio + 1


#
#
#
