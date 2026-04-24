from abc import ABC, abstractmethod
from typing import List, Tuple

from domain.models.order import Order
from domain.types.candle import Candle
from domain.types.direction import Direction
from domain.types.market_action import MarketAction
from domain.types.background import Background
from domain.types.entrypoint import Entrypoint
from domain.types.power import Power


class StrategyOperatorFlat(ABC):
    @abstractmethod
    def uptrend_order(
        self,
        candle: Candle,
        spread: float,
        deposit: float,
        risk_per_trade: float,
        partial_trade_multiplier: float,
        min_volume: float,
        safe_factor: float,
        min_price_delta: float,
        higher_edge:float,
        lower_edge:float,
    ) -> Order: ...

    @abstractmethod
    def downtrend_order(
        self,
        candle: Candle,
        spread: float,
        deposit: float,
        risk_per_trade: float,
        partial_trade_multiplier: float,
        min_volume: float,
        safe_factor: float,
        min_price_delta: float,
        higher_edge:float,
        lower_edge:float,
    ) -> Order: ...

    @abstractmethod
    def entrypoint(
        self,
        candles: List[Candle],
        body_ratio: float,
        shadow_ratio: float,
        higher_edge: float,
        lower_edge: float,
        background: Background,
        service_name: str,
    ) -> Entrypoint: ...

    @abstractmethod
    def on_market_profit(
        self, order: Order, candle: Candle, spread: float
    ) -> Tuple[float, float]: ...

    @abstractmethod
    def off_market_profit(self, candle: Candle, direction: Direction) -> float: ...

    @abstractmethod
    def risk(self, candles: List[Candle], direction: Direction) -> float: ...

    @abstractmethod
    def profit_risk_ratio(self, profit: float, risk: float) -> float: ...

    @abstractmethod
    def check_sl(self, order: Order, candle: Candle, spread: float) -> bool: ...

    @abstractmethod
    def reason(self, order: Order, price_change: float, is_cancelled: bool) -> str: ...

    @abstractmethod
    def action(self, current_state_id: str, last_state_id: str) -> MarketAction: ...

    @abstractmethod
    def is_entry_triggered(self, order: Order, candle: Candle) -> bool: ...

    @abstractmethod
    def is_sl_triggered(self, order: Order, candle: Candle) -> bool: ...

    @abstractmethod
    def is_tp_triggered(self, order: Order, candle: Candle) -> bool: ...

    @abstractmethod
    def is_reversal_candle(self, order: Order, candle: Candle) -> bool: ...

    @abstractmethod
    def history_candles_uptrend(self, candles: List[Candle]) -> List[Candle]: ...

    @abstractmethod
    def history_candles_downtrend(self, candles:List[Candle]) -> List[Candle]: ...
