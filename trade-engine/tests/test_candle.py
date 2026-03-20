import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from domain.types.candle import Candle

is_less_than_test_cases = [
    {
        "name": "0. Self = BUY, other = BUY. Self is shorter",
        "self_candle": Candle(
            high=101, low=99.3, open=100.9, close=100.94, volume=1000
        ),
        "other_candle": Candle(high=101, low=99.2, open=100.9, close=101, volume=1001),
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "expected_is_less_than": True,
    },
    {
        "name": "1. Self = BUY, other = BUY. Self is not shorter",
        "self_candle": Candle(
            high=101, low=99.3, open=100.9, close=100.95, volume=1000
        ),
        "other_candle": Candle(
            high=101, low=99.2, open=100.9, close=100.9, volume=1001
        ),
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "expected_is_less_than": False,
    },
    {
        "name": "2. Self = BUY, other = SELL. Self is shorter",
        "self_candle": Candle(
            high=101, low=99.3, open=100.9, close=100.94, volume=1000
        ),
        "other_candle": Candle(high=101, low=99.2, open=101, close=100.9, volume=100),
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "expected_is_less_than": True,
    },
    {
        "name": "3. Self = BUY, other = SELL. Self is not shorter",
        "self_candle": Candle(
            high=101, low=100.89, open=100.9, close=100.95, volume=1000
        ),
        "other_candle": Candle(
            high=101, low=100.89, open=100.99, close=100.9, volume=1000
        ),
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "expected_is_less_than": False,
    },
]


@pytest.mark.parametrize(
    "case",
    is_less_than_test_cases,
    ids=[c["name"] for c in is_less_than_test_cases],
)
def test_is_less_than(case):
    is_less_than = case["self_candle"].is_less_than(
        case["other_candle"],
        case["body_ratio"],
        case["shadow_ratio"],
    )

    assert is_less_than == case["expected_is_less_than"]


engulfs_test_cases = [
    {
        "name": "0. Self = BUY, other = BUY. Engulfs = True",
        "self_candle": Candle(high=101, low=100.85, open=100.9, close=101, volume=1000),
        "other_candle": Candle(
            high=100.98, low=100.85, open=100.9, close=100.93, volume=1001
        ),
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "expected_engulfs": True,
    },
    {
        "name": "1. Self = BUY, other = BUY. Engulfs = False",
        "self_candle": Candle(high=101, low=100.85, open=100.9, close=101, volume=1000),
        "other_candle": Candle(
            high=100.98, low=100.85, open=100.9, close=100.95, volume=1001
        ),
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "expected_engulfs": False,
    },
    {
        "name": "2. Self = BUY, other = SELL. Engulfs = True",
        "self_candle": Candle(
            high=101.5, low=100.85, open=101, close=100.9, volume=1000
        ),
        "other_candle": Candle(
            high=101.5, low=100.9, open=101, close=100.97, volume=1000
        ),
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "expected_engulfs": True,
    },
    {
        "name": "3. Self = BUY, other = SELL. Engulfs = False",
        "self_candle": Candle(
            high=101.5, low=100.85, open=101, close=100.9, volume=1000
        ),
        "other_candle": Candle(
            high=101.5, low=100.9, open=101, close=100.96, volume=1000
        ),
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "expected_engulfs": False,
    },
]


@pytest.mark.parametrize(
    "case",
    engulfs_test_cases,
    ids=[c["name"] for c in engulfs_test_cases],
)
def test_engulfs(case):
    engulfs = case["self_candle"].engulfs(
        case["other_candle"],
        case["body_ratio"],
        case["shadow_ratio"],
    )

    assert engulfs == case["expected_engulfs"]
