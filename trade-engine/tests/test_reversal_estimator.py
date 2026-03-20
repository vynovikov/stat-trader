import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from domain.types.candle import Candle
from domain.types.category import Category
from domain.types.direction import Direction
from services.estimator.reversal_estimator import ReversalEstimator

estimate_test_cases = [
    {
        "name": "0. Not enough candles",
        "candles": [
            Candle(high=100, low=98, open=99, close=99, volume=1000),
            Candle(high=101, low=99, open=100, close=100, volume=1001),
        ],
        "direction": Direction.UP,
        "from_candle_id": 2,
        "expected_category": Category.NONE,
        "expected_profit": 0.0,
        "expected_loss": 0.0,
        "expected_profit_loss_ratio": 0.0,
    },
    {
        "name": "1. Uptrend. Candles increasing",
        "candles": [
            Candle(high=100, low=98, open=99, close=99, volume=1000),
            Candle(high=101, low=99, open=100, close=100, volume=1001),
            Candle(high=102, low=100, open=101, close=103, volume=1002),
            Candle(high=105, low=102, open=103, close=105, volume=1003),
            Candle(high=108, low=105, open=105, close=107, volume=1004),
            Candle(high=108, low=101, open=107, close=103, volume=1005),
        ],
        "direction": Direction.UP,
        "from_candle_id": 2,
        "expected_category": Category.WISHFUL,
        "expected_profit": -2.0,
        "expected_loss": 1.0,
        "expected_profit_loss_ratio": -200,
    },
    {
        "name": "2. Uptrend. Third candle stops trend. Last close < first open",
        "candles": [
            Candle(high=100, low=98, open=99, close=100, volume=1000),
            Candle(high=102, low=99, open=100, close=101, volume=1001),
            Candle(high=102, low=99, open=101, close=100, volume=1003),
        ],
        "direction": Direction.UP,
        "from_candle_id": 2,
        "expected_category": Category.BEAR,
        "expected_profit": 1.0,
        "expected_loss": 1.0,
        "expected_profit_loss_ratio": 100,
    },
    {
        "name": "3. Uptrend. Fourth candle stops trend. Last close < first open",
        "candles": [
            Candle(high=100, low=98, open=99, close=100, volume=1000),
            Candle(high=102, low=99, open=100, close=101, volume=1001),
            Candle(high=103, low=100, open=101, close=102, volume=1003),
            Candle(high=103, low=99, open=102, close=100, volume=1003),
        ],
        "direction": Direction.UP,
        "from_candle_id": 2,
        "expected_category": Category.WISHFUL,
        "expected_profit": -1,
        "expected_loss": 2.0,
        "expected_profit_loss_ratio": -50,
        "expected_reversal_trend_candles": 2,
    },
    {
        "name": "4. Downtrend. Candles decreasing",
        "candles": [
            Candle(high=100, low=97, open=99, close=98, volume=1000),
            Candle(high=99, low=96, open=98, close=97, volume=1001),
            Candle(high=98, low=95, open=97, close=96, volume=1002),
            Candle(high=97, low=94, open=96, close=95, volume=1003),
            Candle(high=96, low=93, open=95, close=94, volume=1004),
            Candle(high=97, low=93, open=94, close=95, volume=1005),
        ],
        "direction": Direction.DOWN,
        "expected_category": Category.WISHFUL,
        "from_candle_id": 2,
        "expected_profit": -1.0,
        "expected_loss": 2.0,
        "expected_profit_loss_ratio": -50,
    },
    {
        "name": "5. Downtrend. Third candle stops trend. Last close < first open",
        "candles": [
            Candle(high=100, low=97, open=99, close=98, volume=1000),
            Candle(high=99, low=96, open=98, close=97, volume=1001),
            Candle(high=99, low=96, open=97, close=98, volume=1002),
        ],
        "direction": Direction.DOWN,
        "expected_category": Category.BULL,
        "from_candle_id": 2,
        "expected_profit": 1.0,
        "expected_loss": 1.0,
        "expected_profit_loss_ratio": 100,
    },
    {
        "name": "6. Downtrend. Fourth candle stops trend. Last close < first open",
        "candles": [
            Candle(high=100, low=97, open=99, close=98, volume=1000),
            Candle(high=99, low=96, open=98, close=97, volume=1001),
            Candle(high=99, low=96, open=97, close=96, volume=1002),
            Candle(high=99, low=96, open=96, close=97, volume=1003),
        ],
        "direction": Direction.DOWN,
        "expected_category": Category.WISHFUL,
        "from_candle_id": 2,
        "expected_profit": -1.0,
        "expected_loss": 1.0,
        "expected_profit_loss_ratio": -100,
    },
]


@pytest.mark.parametrize(
    "case",
    estimate_test_cases,
    ids=[c["name"] for c in estimate_test_cases],
)
def test_estimate(case):
    estimator = ReversalEstimator()

    estimation = estimator.estimate(
        candles=case["candles"],
        direction=case["direction"],
        from_candle_id=case["from_candle_id"],
    )

    assert (
        estimation.category == case["expected_category"]
    ), f"Profit mismatch in case {case['name']}"

    assert round(estimation.profit, 2) == round(
        case["expected_profit"], 2
    ), f"Profit mismatch in case {case['name']}"

    assert round(estimation.risk, 2) == round(
        case["expected_risk"], 2
    ), f"Risk mismatch in case {case['name']}"

    assert round(estimation.profit_risk_ratio, 2) == round(
        case["expected_profit_risk_ratio"], 2
    ), f"Profit_Risk_Ratio mismatch in case {case['name']}"
