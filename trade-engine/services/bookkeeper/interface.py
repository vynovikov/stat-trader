from abc import ABC, abstractmethod


class Bookkeeper(ABC):
    @abstractmethod
    def calculate_volume(
        self,
        entry_price: float,
        sl: float,
        deposit: float,
        risk_per_trade: float,
        min_volume: float,
        safe_factor: float,
    ) -> float: ...

    @abstractmethod
    def profit(self, price_difference: float, volume: float) -> float: ...
