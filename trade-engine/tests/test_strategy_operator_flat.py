import pytest
import logging

from typing import Any, Dict, List
from logging import LoggerAdapter

from domain.types.candle import Candle
from domain.types.background import Background
from domain.types.entrypoint import Entrypoint

from services.metric_repository.mock_metric_repository import MockMetricRepository
from services.bookkeeper.leveraged_bookkeeper import LeveragedBookkeeper
from services.strategy_operator.strategy_operator_flat import (
    StrategyOperatorFlatImpl,
)

def trade_engine_logger(label: str) -> LoggerAdapter:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)

    formatter = logging.Formatter("    - %(levelname)s: [%(engine_id)s] %(message)s")
    stream_handler.setFormatter(formatter)

    base_logger = logging.getLogger(label)
    base_logger.setLevel(logging.INFO)
    base_logger.addHandler(stream_handler)

    logger = logging.LoggerAdapter(base_logger, {"engine_id": label})

    return logger

entrypoint_test_cases: List[Dict[str, Any]] = [
    {
        "name":"0. Candle.high > higher_edge. Close in margin. UP candle",
        "candle":Candle(open=100.8, close=100.98, high=101.05, low=100.7),
        "higher_edge":101,
        "lower_edge":100.4,
        "margin":0.05,
        "service_name":"strategy_flat",
        "expected_entrypoint": Entrypoint.SELL,
    },
    {
        "name":"1. Candle.high > higher_edge. Close in margin. DOWN candle",
        "candle":Candle(open=100.99, close=100.98, high=101.05, low=100.9),
        "higher_edge":101,
        "lower_edge":100.4,
        "margin":0.05,
        "service_name":"strategy_flat",
        "expected_entrypoint": Entrypoint.SELL,
    },
    {
        "name":"2. Candle.high > higher_edge. Close out of margin. DOWN candle",
        "candle":Candle(open=100.99, close=100.92, high=101.05, low=100.85),
        "higher_edge":101,
        "lower_edge":100.4,
        "margin":0.05,
        "service_name":"strategy_flat",
        "expected_entrypoint": Entrypoint.UNKNOWN,
    },
    {
        "name":"3. Candle.low < lower_edge. Close in margin. UP candle",
        "candle":Candle(open=100.41, close=100.42, high=100.55, low=100.37),
        "higher_edge":101,
        "lower_edge":100.4,
        "margin":0.05,
        "service_name":"strategy_flat",
        "expected_entrypoint": Entrypoint.BUY,
    },
    {
        "name":"4. Candle.low < lower_edge. Close in margin. DOWN candle",
        "candle":Candle(open=100.42, close=100.41, high=100.55, low=100.37),
        "higher_edge":101,
        "lower_edge":100.4,
        "margin":0.05,
        "service_name":"strategy_flat",
        "expected_entrypoint": Entrypoint.BUY,
    },
    {
        "name":"5. Candle.low < lower_edge. Close out of margin. DOWN candle",
        "candle":Candle(open=100.6, close=100.5, high=100.65, low=100.37),
        "higher_edge":101,
        "lower_edge":100.4,
        "margin":0.05,
        "service_name":"strategy_flat",
        "expected_entrypoint": Entrypoint.UNKNOWN,
    }
]


@pytest.mark.parametrize(
    "case", entrypoint_test_cases, ids=[c["name"] for c in entrypoint_test_cases]
)
def test_strategy_operator_entrypoint(case):
    logger = trade_engine_logger("strategy_con_v6")
    leveraged_bookkeeper = LeveragedBookkeeper(leverage=10)
    metric_repository = MockMetricRepository()
    strategy_operator = StrategyOperatorFlatImpl(
        bookkeeper=leveraged_bookkeeper,
        metric_repository=metric_repository,
        logger=logger,
        )

    entrypoint = strategy_operator.entrypoint(
        candle=case["candle"],
        higher_edge=case["higher_edge"],
        lower_edge=case["lower_edge"],
        margin=case["margin"],
        service_name=case["service_name"],
    )

    assert (
        entrypoint == case["expected_entrypoint"]
    ), f"expected_entrypoint {case["expected_entrypoint"]} but got {entrypoint}"
