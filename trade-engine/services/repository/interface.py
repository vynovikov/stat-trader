from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from domain.models.nearest_neighbor import NearestNeighbor
from domain.models.segment import Segment
from domain.types.payload import Payload


class Repository(ABC):
    @abstractmethod
    def upsert(self, id: int, segment: Segment) -> None: ...

    @abstractmethod
    def neighbors(self, id: int, limit: int) -> List[NearestNeighbor]: ...

    @abstractmethod
    def count_all(self) -> int: ...

    @abstractmethod
    def get_payload(self, id: int) -> Payload: ...

    @abstractmethod
    def update_payload(self, id: int, payload: Payload = Payload()) -> None: ...

    @abstractmethod
    def delete_vector(self, id: int) -> None: ...

    @abstractmethod
    def clean_expired(self, when: datetime) -> None: ...

    @abstractmethod
    def clear_collection(self) -> None: ...
