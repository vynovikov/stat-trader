from dataclasses import dataclass, field

from domain.types.payload import Payload


@dataclass
class NearestNeighbor:
    id: int = 0
    score: float = 0.0
    payload: Payload = field(default_factory=Payload)
