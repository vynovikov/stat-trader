import numpy as np
from qdrant_client.http.models import PointStruct

from domain.models.segment import Segment
from domain.models.trade_params import TradeParams


def segment_to_point(id: int, segment: Segment) -> PointStruct:
    """Convert a segment to Qdrant PointStruct."""
    vector = segment.get_pattern_vector()
    return PointStruct(
        id=id,
        vector=vector.tolist(),
        payload={
            "direction": segment.direction(),
            "category": segment.category(),
            "profit": segment.profit(),
            "risk": segment.risk(),
            "profit_risk_ratio": segment.profit_risk_ratio(),
            "candles_num": segment.candles_num(),
            "created_at": segment.created_at(),
            "expire_at": segment.expire_at(),
        },
    )
