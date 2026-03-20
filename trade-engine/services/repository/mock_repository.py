from datetime import datetime
from typing import List

from domain.models.nearest_neighbor import NearestNeighbor
from domain.models.segment import Segment
from domain.types.payload import Payload
from services.repository.interface import Repository


class MockRepository(Repository):
    def upsert(self, id: int, segment: Segment) -> None:
        pass

    def neighbors(self, id: int, limit: int) -> List[NearestNeighbor]:
        return []

    def count_all(self) -> int:
        return 0

    def get_payload(self, id: int) -> Payload:
        return Payload()

    def update_payload(self, id: int, payload: Payload = Payload()) -> None:
        pass

    def delete_vector(self, id: int) -> None:
        pass

    def clean_expired(self, when: datetime) -> None:
        pass

    def clear_collection(self) -> None:
        pass
