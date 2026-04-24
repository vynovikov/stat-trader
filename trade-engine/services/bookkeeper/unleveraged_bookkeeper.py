from services.bookkeeper.interface import Bookkeeper


class UnleveragedBookkeeper(Bookkeeper):
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
        volume = (deposit * risk_per_trade) / abs(entry_price - sl)

        if volume > deposit:
            volume = deposit

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
