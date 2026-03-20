from abc import ABC, abstractmethod
from typing import List

from domain.models.order import Order
from domain.types.candle import Candle
from domain.types.payload import Payload


class CounterOperator(ABC):
    @abstractmethod
    def last_id(self) -> int: ...

    @abstractmethod
    def last_id_inc(self) -> None: ...

    @abstractmethod
    def last_id_dec(self) -> None: ...

    @abstractmethod
    def neighbor_limit(self) -> int: ...

    @abstractmethod
    def cooldown_counter(self) -> int: ...

    @abstractmethod
    def cooldown_set(self) -> None: ...

    @abstractmethod
    def cooldown_dec(self) -> bool: ...
