from datetime import datetime
from typing import NamedTuple


class Candle(NamedTuple):
    high: float = 0.0
    low: float = 0.0
    open: float = 0.0
    close: float = 0.0
    volume: float = 0.0
    ma_50: float = 0.0
    ma_200: float = 0.0
    open_time: datetime = datetime.min
    close_time: datetime = datetime.min
    is_sl_triggered: bool = False

    def is_UP(self) -> bool:
        return self.close > self.open

    def is_DOWN(self) -> bool:
        return self.close < self.open

    def body_len(self) -> float:
        return abs(self.open - self.close)

    def shadow_len(self) -> float:
        return self.high - self.low

    def is_less_than(
        self,
        other: "Candle",
        body_ratio: float,
        shadow_ratio: float,
    ) -> bool:

        if self.high - self.low < 0 or other.high - other.low < 0:
            return False

        self_body_length = abs(self.open - self.close)
        self_shadow_length = self.high - self.low
        other_body_length = abs(other.open - other.close)
        other_shadow_length = other.high - other.low

        return (
            other_body_length * body_ratio > self_body_length
            and other_shadow_length * shadow_ratio > self_shadow_length
        )

    def engulfs(
        self,
        other: "Candle",
        body_ratio: float,
        shadow_ratio: float,
    ) -> bool:

        if self.high - self.low < 0 or other.high - other.low < 0:
            return False

        self_body_length = abs(self.open - self.close)
        self_shadow_length = self.high - self.low
        other_body_length = abs(other.open - other.close)
        other_shadow_length = other.high - other.low

        return (
            self_body_length * body_ratio > other_body_length
            and self_shadow_length * shadow_ratio > other_shadow_length
        )
