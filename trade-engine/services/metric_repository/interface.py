from abc import ABC, abstractmethod

from typing import List, Optional
from datetime import datetime

from domain.types.candle import Candle
from domain.types.candle_action import CandleAction


class MetricRepository(ABC):
    @abstractmethod
    def insert_trade_real(
        self,
        id: int,
        symbol: str,
        open_time: datetime,
        engine_id: str,
        candle_action: CandleAction,
        reason: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        volume: float,
        profit: float,
    ) -> None: ...

    @abstractmethod
    def insert_candles_all(
        self,
        symbol: str,
        timeframe: str,
        candles: List[Candle],
    ) -> None: ...

    @abstractmethod
    def insert_candles_traded(
        self,
        symbol: str,
        timeframe: str,
        candles: List[Candle],
        engine_id: str,
        trade_id: Optional[int] = None,
    ) -> None: ...

    @abstractmethod
    def insert_trade_historical(
        self,
        id: int,
        symbol: str,
        open_time: datetime,
        engine_id: str,
        candle_action: CandleAction,
        reason: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        volume: float,
        profit: float,
    ) -> None: ...

    @abstractmethod
    def insert_candles_historical(
        self,
        symbol: str,
        timeframe: str,
        candles: List[Candle],
        engine_id: str,
        trade_id: Optional[int] = None,
    ) -> None: ...

    @abstractmethod
    def insert_log(
        self,
        created_at: datetime,
        log_level: str,
        service_name: str,
        log_string: str,
    ) -> None: ...

    @abstractmethod
    def truncate_historical_tables(self) -> None: ...
