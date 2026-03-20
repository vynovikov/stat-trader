from contextlib import nullcontext
from datetime import datetime
from typing import List

import pandas as pd
import pytest

# from config.config import qdrant_config
from domain.models.segment import Segment
from domain.models.trade_params import TradeParams
from domain.types.category import Category
from domain.types.direction import Direction
from domain.types.payload import Payload
from marker.marker import Marker
from services.estimator.reversal_estimator import ReversalEstimator
from services.repository.mock_repository import MockRepository

# from services.repository import QdrantRepository
from utils.read_data import read_data

pytest.skip("Qdrant config not configured", allow_module_level=True)


# def get_repository(symbol: str) -> QdrantRepository:
#    config = qdrant_config
#    repository = QdrantRepository(symbol=symbol, config=config)
#    return repository


def get_repository(symbol: str) -> MockRepository:
    return MockRepository()


def get_segments(df: pd.DataFrame) -> List[Segment]:
    estimator = ReversalEstimator()
    marker = Marker(estimator=estimator, a_len=4)
    segments = marker.mark(df)
    return segments


upsert_test_cases = [
    {
        "name": "0. No initial vectors",
        "initial_vectors_num": 0,
        "vectors_to_add": 1,
        "upsert_existing_id": -1,
        "expected_rewritten_payload": Payload(
            category=Category.NONE, profit=0.0, risk=0.0, profit_risk_ratio=0.0
        ),
        "expected_vectors_num": 1,
    },
    {
        "name": "1. Have initial vectors. Add one more",
        "initial_vectors_num": 10,
        "vectors_to_add": 1,
        "upsert_existing_id": -1,
        "expected_rewritten_payload": Payload(
            category=Category.NONE, profit=0.0, risk=0.0, profit_risk_ratio=0.0
        ),
        "expected_vectors_num": 11,
    },
    {
        "name": "2. Have initial vectors. Add several more",
        "initial_vectors_num": 10,
        "vectors_to_add": 5,
        "upsert_existing_id": -1,
        "expected_rewritten_payload": Payload(
            category=Category.NONE, profit=0.0, risk=0.0, profit_risk_ratio=0.0
        ),
        "expected_vectors_num": 15,
    },
    {
        "name": "3. Have initial vectors. Re-add existing vector",
        "initial_vectors_num": 10,
        "vectors_to_add": 0,
        "upsert_existing_id": 0,
        "expected_rewritten_payload": Payload(
            category=Category.NONE, profit=0.0, risk=0.0, profit_risk_ratio=0.0
        ),
        "expected_vectors_num": 10,
    },
]


@pytest.mark.parametrize(
    "case",
    upsert_test_cases,
    ids=[c["name"] for c in upsert_test_cases],
)
def test_upsert(case):
    qdrant_repository = get_repository(symbol="test")
    qdrant_repository.clear_collection()

    base_df = read_data(
        input_file="data/candles/BTCUSDT/ma_added/BTCUSDT_5m_ma.csv",
        offset_hours=0,
        limit_hours=100,
    )

    segments = get_segments(base_df)

    for idx, segment in enumerate(segments[: case["initial_vectors_num"]]):
        segment.update_pattern_characteristics(
            candles_limit=4,
            ma_50s=base_df["ma_50"].tolist(),
            ma_200s=base_df["ma_200"].tolist(),
        )

        qdrant_repository.upsert(id=idx, segment=segment)

    if case["initial_vectors_num"] > case["upsert_existing_id"] >= 0:
        segment = segments[case["upsert_existing_id"]]
        segment.Params = TradeParams(
            direction=Direction.UNKNOWN, category=Category.NONE
        )
        qdrant_repository.upsert(
            id=case["upsert_existing_id"],
            segment=segment,
        )

    for idx, segment in enumerate(
        segments[
            case["initial_vectors_num"] : case["initial_vectors_num"]
            + case["vectors_to_add"]
        ],
        start=case["initial_vectors_num"],
    ):
        segment.update_pattern_characteristics(
            candles_limit=4,
            ma_50s=base_df["ma_50"].tolist(),
            ma_200s=base_df["ma_200"].tolist(),
        )

        qdrant_repository.upsert(id=idx, segment=segment)

    assert qdrant_repository.count_all() == case["expected_vectors_num"]

    if case["upsert_existing_id"] >= 0:
        payload = qdrant_repository.get_payload(id=case["upsert_existing_id"])
        assert payload == case["expected_rewritten_payload"]


neighbors_test_cases = [
    {
        "name": "0. No initial vectors",
        "initial_vectors_num": 0,
        "base_vector_id": 1,
        "neighbors_limit": 5,
        "expected_error": True,
        "expected_neighbors_ids": [],
    },
    {
        "name": "1. Have initial vectors. Vector ID not in DB.",
        "initial_vectors_num": 5,
        "base_vector_id": 6,
        "neighbors_limit": 5,
        "expected_error": True,
        "expected_neighbors_ids": [],
    },
    {
        "name": "2. Have initial vectors. Vector ID in DB. Limit < count",
        "initial_vectors_num": 30,
        "base_vector_id": 1,
        "neighbors_limit": 5,
        "expected_error": False,
        "expected_neighbors_ids": [28, 15, 26, 24, 25],
    },
    {
        "name": "3. Have initial vectors. Vector ID in DB. Limit > count",
        "initial_vectors_num": 3,
        "base_vector_id": 1,
        "neighbors_limit": 5,
        "expected_error": False,
        "expected_neighbors_ids": [0, 2],
    },
]


@pytest.mark.parametrize(
    "case",
    neighbors_test_cases,
    ids=[c["name"] for c in neighbors_test_cases],
)
def test_neighbors(case):
    qdrant_repository = get_repository(symbol="test")
    qdrant_repository.clear_collection()

    base_df = read_data(
        input_file="data/candles/BTCUSDT/ma_added/BTCUSDT_5m_ma.csv",
        offset_hours=0,
        limit_hours=100,
    )

    segments = get_segments(base_df)

    for idx, segment in enumerate(segments[: case["initial_vectors_num"]]):
        segment.update_pattern_characteristics(
            candles_limit=4,
            ma_50s=base_df["ma_50"].tolist(),
            ma_200s=base_df["ma_200"].tolist(),
        )

        qdrant_repository.upsert(id=idx, segment=segment)

    neighbors = []

    with pytest.raises(Exception) if case["expected_error"] == True else nullcontext():
        neighbors = qdrant_repository.neighbors(
            id=case["base_vector_id"], limit=case["neighbors_limit"]
        )

    for idx, neighbor in enumerate(neighbors):
        assert neighbor.id in case["expected_neighbors_ids"]


update_payload_test_cases = [
    {
        "name": "0. No initial vectors",
        "initial_vectors_num": 0,
        "base_vector_id": 1,
        "payload": Payload(
            category=Category.NONE, profit=0.0, risk=0.0, profit_risk_ratio=0.0
        ),
        "expected_error": False,
        "expected_payload": Payload(),
    },
    {
        "name": "1. Have initial vectors. Vector ID not in DB.",
        "initial_vectors_num": 5,
        "base_vector_id": 6,
        "payload": Payload(
            category=Category.NONE, profit=0.0, risk=0.0, profit_risk_ratio=0.0
        ),
        "expected_error": False,
        "expected_payload": Payload(),
    },
    {
        "name": "2. Have initial vectors. Vector ID is in DB.",
        "initial_vectors_num": 5,
        "base_vector_id": 1,
        "payload": Payload(
            category=Category.NONE, profit=0.0, risk=0.0, profit_risk_ratio=0.0
        ),
        "expected_error": False,
        "expected_payload": Payload(
            category=Category.NONE, profit=0.0, risk=0.0, profit_risk_ratio=0.0
        ),
    },
]


@pytest.mark.parametrize(
    "case",
    update_payload_test_cases,
    ids=[c["name"] for c in update_payload_test_cases],
)
def test_update_payload(case):
    qdrant_repository = get_repository(symbol="test")
    qdrant_repository.clear_collection()

    base_df = read_data(
        input_file="data/candles/BTCUSDT/ma_added/BTCUSDT_5m_ma.csv",
        offset_hours=0,
        limit_hours=100,
    )

    segments = get_segments(base_df)

    for idx, segment in enumerate(segments[: case["initial_vectors_num"]]):
        segment.update_pattern_characteristics(
            candles_limit=4,
            ma_50s=base_df["ma_50"].tolist(),
            ma_200s=base_df["ma_200"].tolist(),
        )

        qdrant_repository.upsert(id=idx, segment=segment)

    payload = Payload()
    with pytest.raises(Exception) if case["expected_error"] == True else nullcontext():
        qdrant_repository.update_payload(
            id=case["base_vector_id"], payload=case["payload"]
        )
        payload = qdrant_repository.get_payload(id=case["base_vector_id"])

    assert payload == case["expected_payload"]


clean_expired_test_cases = [
    {
        "name": "0. No initial vectors",
        "initial_vectors_num": 0,
        "vectors_to_expire": 0,
        "expected_vectors_num": 0,
    },
    {
        "name": "1. Have initial vectors. None expired",
        "initial_vectors_num": 5,
        "vectors_to_expire": 0,
        "expected_vectors_num": 5,
    },
    {
        "name": "2. Have initial vectors. Some expired",
        "initial_vectors_num": 30,
        "vectors_to_expire": 5,
        "expected_vectors_num": 25,
    },
    {
        "name": "3. Have initial vectors. All expired",
        "initial_vectors_num": 10,
        "vectors_to_expire": 10,
        "expected_vectors_num": 0,
    },
]


@pytest.mark.parametrize(
    "case",
    clean_expired_test_cases,
    ids=[c["name"] for c in clean_expired_test_cases],
)
def test_clean_expired(case):
    qdrant_repository = get_repository(symbol="test")
    qdrant_repository.clear_collection()

    base_df = read_data(
        input_file="data/candles/BTCUSDT/ma_added/BTCUSDT_5m_ma.csv",
        offset_hours=0,
        limit_hours=100,
    )

    segments = get_segments(base_df)

    for idx, segment in enumerate(segments[: case["initial_vectors_num"]]):
        segment.update_pattern_characteristics(
            candles_limit=4,
            ma_50s=base_df["ma_50"].tolist(),
            ma_200s=base_df["ma_200"].tolist(),
        )

        qdrant_repository.upsert(id=idx, segment=segment)

    expiration_time = datetime.min

    if case["vectors_to_expire"] > 0:
        expiration_time = segments[
            case["vectors_to_expire"] - 1 if case["vectors_to_expire"] > 0 else 0
        ].expire_at()

    qdrant_repository.clean_expired(expiration_time)

    assert qdrant_repository.count_all() == case["expected_vectors_num"]


delete_vector_test_cases = [
    {
        "name": "0. No initial vectors",
        "initial_vectors_num": 0,
        "expected_vectors_num": 0,
    },
    {
        "name": "1. Have initial vectors",
        "initial_vectors_num": 10,
        "expected_vectors_num": 9,
    },
]


@pytest.mark.parametrize(
    "case",
    delete_vector_test_cases,
    ids=[c["name"] for c in delete_vector_test_cases],
)
def test_delete_vector(case):
    qdrant_repository = get_repository(symbol="test")
    qdrant_repository.clear_collection()

    base_df = read_data(
        input_file="data/candles/BTCUSDT/ma_added/BTCUSDT_5m_ma.csv",
        offset_hours=0,
        limit_hours=100,
    )

    segments = get_segments(base_df)

    for idx, segment in enumerate(segments[: case["initial_vectors_num"]]):
        segment.update_pattern_characteristics(
            candles_limit=4,
            ma_50s=base_df["ma_50"].tolist(),
            ma_200s=base_df["ma_200"].tolist(),
        )

        qdrant_repository.upsert(id=idx, segment=segment)

    qdrant_repository.delete_vector(
        case["initial_vectors_num"] - 1 if case["initial_vectors_num"] > 0 else 0
    )

    assert qdrant_repository.count_all() == case["expected_vectors_num"]
