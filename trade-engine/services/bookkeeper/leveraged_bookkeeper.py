import math

from services.bookkeeper.interface import Bookkeeper


class LeveragedBookkeeper(Bookkeeper):
    def __init__(self, leverage: int) -> None:
        self.leverage = leverage

    def calculate_volume(
        self,
        entry_price: float,
        sl: float,
        deposit: float,
        risk_per_trade: float,
        partial_trade_multiplier: float,
        min_volume: float,
        safe_factor: float,
    ) -> float:
        """
        Calculate volume based on entry price, stop loss and deposit.
        """
        sl_price_change = abs(entry_price - sl)

        max_volume = (
            math.floor(deposit * self.leverage * 1000 * (1 - safe_factor) / entry_price)
            / 1000
        )

        volume_raw = deposit * risk_per_trade*partial_trade_multiplier / sl_price_change

        volume = math.floor(volume_raw * 1000) / 1000

        match True:
            case _ if volume_raw < min_volume:
                volume = min_volume
            case _ if volume_raw > max_volume:
                volume = max_volume

        return volume

    def profit(
        self,
        price_difference: float,
        volume: float,
    ) -> float:
        """
        Calculate profit based on price difference, volume and entry price.
        """
        profit = price_difference * volume

        return profit
