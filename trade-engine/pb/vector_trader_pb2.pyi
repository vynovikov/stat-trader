import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CandleAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NONE: _ClassVar[CandleAction]
    BUY: _ClassVar[CandleAction]
    SELL: _ClassVar[CandleAction]

class MarketAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    HOLD: _ClassVar[MarketAction]
    OPEN: _ClassVar[MarketAction]
    CLOSE: _ClassVar[MarketAction]
    CLOSE_THEN_OPEN: _ClassVar[MarketAction]
NONE: CandleAction
BUY: CandleAction
SELL: CandleAction
HOLD: MarketAction
OPEN: MarketAction
CLOSE: MarketAction
CLOSE_THEN_OPEN: MarketAction

class LastNRequest(_message.Message):
    __slots__ = ("symbol", "interval", "limit")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    interval: str
    limit: int
    def __init__(self, symbol: _Optional[str] = ..., interval: _Optional[str] = ..., limit: _Optional[int] = ...) -> None: ...

class LastNResponse(_message.Message):
    __slots__ = ("candles",)
    CANDLES_FIELD_NUMBER: _ClassVar[int]
    candles: _containers.RepeatedCompositeFieldContainer[Candle]
    def __init__(self, candles: _Optional[_Iterable[_Union[Candle, _Mapping]]] = ...) -> None: ...

class IntervalCandlesRequest(_message.Message):
    __slots__ = ("symbol", "interval", "from_timestamp", "to_timestamp")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    FROM_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TO_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    interval: str
    from_timestamp: int
    to_timestamp: int
    def __init__(self, symbol: _Optional[str] = ..., interval: _Optional[str] = ..., from_timestamp: _Optional[int] = ..., to_timestamp: _Optional[int] = ...) -> None: ...

class IntervalCandlesResponse(_message.Message):
    __slots__ = ("candles",)
    CANDLES_FIELD_NUMBER: _ClassVar[int]
    candles: _containers.RepeatedCompositeFieldContainer[Candle]
    def __init__(self, candles: _Optional[_Iterable[_Union[Candle, _Mapping]]] = ...) -> None: ...

class DecideRequest(_message.Message):
    __slots__ = ("candle", "spread", "balance")
    CANDLE_FIELD_NUMBER: _ClassVar[int]
    SPREAD_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    candle: Candle
    spread: float
    balance: float
    def __init__(self, candle: _Optional[_Union[Candle, _Mapping]] = ..., spread: _Optional[float] = ..., balance: _Optional[float] = ...) -> None: ...

class DecideResponse(_message.Message):
    __slots__ = ("market_action", "order", "profit")
    MARKET_ACTION_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    PROFIT_FIELD_NUMBER: _ClassVar[int]
    market_action: MarketAction
    order: Order
    profit: float
    def __init__(self, market_action: _Optional[_Union[MarketAction, str]] = ..., order: _Optional[_Union[Order, _Mapping]] = ..., profit: _Optional[float] = ...) -> None: ...

class OpenOrderRequest(_message.Message):
    __slots__ = ("symbol", "order")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    order: Order
    def __init__(self, symbol: _Optional[str] = ..., order: _Optional[_Union[Order, _Mapping]] = ...) -> None: ...

class OpenOrderResponse(_message.Message):
    __slots__ = ("order_id",)
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    order_id: str
    def __init__(self, order_id: _Optional[str] = ...) -> None: ...

class CloseOrderRequest(_message.Message):
    __slots__ = ("symbol",)
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    def __init__(self, symbol: _Optional[str] = ...) -> None: ...

class CloseOrderResponse(_message.Message):
    __slots__ = ("profit",)
    PROFIT_FIELD_NUMBER: _ClassVar[int]
    profit: float
    def __init__(self, profit: _Optional[float] = ...) -> None: ...

class Candle(_message.Message):
    __slots__ = ("open", "high", "low", "close", "volume", "open_time", "close_time")
    OPEN_FIELD_NUMBER: _ClassVar[int]
    HIGH_FIELD_NUMBER: _ClassVar[int]
    LOW_FIELD_NUMBER: _ClassVar[int]
    CLOSE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    OPEN_TIME_FIELD_NUMBER: _ClassVar[int]
    CLOSE_TIME_FIELD_NUMBER: _ClassVar[int]
    open: float
    high: float
    low: float
    close: float
    volume: float
    open_time: _timestamp_pb2.Timestamp
    close_time: _timestamp_pb2.Timestamp
    def __init__(self, open: _Optional[float] = ..., high: _Optional[float] = ..., low: _Optional[float] = ..., close: _Optional[float] = ..., volume: _Optional[float] = ..., open_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., close_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Order(_message.Message):
    __slots__ = ("entry", "sl", "tp", "candle_action", "volume")
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    SL_FIELD_NUMBER: _ClassVar[int]
    TP_FIELD_NUMBER: _ClassVar[int]
    CANDLE_ACTION_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    entry: float
    sl: float
    tp: float
    candle_action: CandleAction
    volume: float
    def __init__(self, entry: _Optional[float] = ..., sl: _Optional[float] = ..., tp: _Optional[float] = ..., candle_action: _Optional[_Union[CandleAction, str]] = ..., volume: _Optional[float] = ...) -> None: ...
