import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from domain.models.segment import Segment
from domain.models.trade_params import TradeParams
from domain.types.candle import Candle
from domain.types.direction import Direction

calc_sl_test_cases = [
    {
        "name": "0. Empty trend - no SL calculation",
        "trend_candles": [],
        "direction": Direction.UP,
        "expected_sl": 0.0,  # Default value from TradeParams
    },
    {
        "name": "1. Single candle uptrend",
        "trend_candles": [
            Candle(high=1.05, low=1.00, open=1.01, close=1.04, volume=1000),
        ],
        "direction": Direction.UP,
        "expected_sl": 0.01,
    },
    {
        "name": "2. Single candle downtrend",
        "trend_candles": [
            Candle(high=1.05, low=1.00, open=1.04, close=1.01, volume=1000),
        ],
        "direction": Direction.DOWN,
        "expected_sl": 0.01,
    },
    {
        "name": "3. Multiple candles uptrend",
        "trend_candles": [
            Candle(high=1.05, low=1.00, open=1.01, close=1.04, volume=1000),
            Candle(high=1.08, low=1.02, open=1.04, close=1.07, volume=1000),
            Candle(high=1.10, low=0.98, open=1.07, close=1.09, volume=1000),
        ],
        "direction": Direction.UP,
        "expected_sl": 0.03,
    },
    {
        "name": "4. Multiple candles downtrend",
        "trend_candles": [
            Candle(high=1.05, low=1.00, open=1.04, close=1.01, volume=1000),
            Candle(high=1.12, low=0.98, open=1.01, close=0.99, volume=1000),
            Candle(high=1.02, low=0.95, open=0.99, close=0.96, volume=1000),
        ],
        "direction": Direction.DOWN,
        "expected_sl": 0.08,
    },
    {
        "name": "5. Unknown direction",
        "trend_candles": [
            Candle(high=1.05, low=1.00, open=1.01, close=1.04, volume=1000),
        ],
        "direction": Direction.UNKNOWN,
        "expected_sl": float("inf"),
    },
]


@pytest.mark.parametrize(
    "case", calc_sl_test_cases, ids=[c["name"] for c in calc_sl_test_cases]
)
def test_calc_sl_table_driven(case):
    """
    Тестирование метода calc_sl для расчета Stop Loss
    """
    # ARRANGE
    segment = Segment()
    segment.Params = TradeParams(direction=case["direction"])
    segment.Trend = case["trend_candles"]

    # ACT
    segment.calc_sl()

    # ASSERT
    assert round(segment.Params.sl, 2) == round(case["expected_sl"], 2), (
        f"Case: {case['name']} - Expected SL: {case['expected_sl']}, "
        f"but got: {segment.Params.sl}"
    )


# Test cases for calc_tp method
calc_tp_test_cases = [
    {
        "name": "0. Empty trend",
        "trend_candles": [],
        "direction": Direction.UP,
        "expected_tp": 0.0,
    },
    {
        "name": "1. Single candle uptrend",
        "trend_candles": [
            Candle(high=1.05, low=1.00, open=1.01, close=1.04, volume=1000),
        ],
        "direction": Direction.UP,
        "expected_tp": 0.04,
    },
    {
        "name": "2. Single candle downtrend",
        "trend_candles": [
            Candle(high=1.05, low=1.00, open=1.04, close=1.01, volume=1000),
        ],
        "direction": Direction.DOWN,
        "expected_tp": 0.01,
    },
    {
        "name": "3. Multiple candles uptrend",
        "trend_candles": [
            Candle(high=1.05, low=1.00, open=1.01, close=1.04, volume=1000),
            Candle(high=1.08, low=1.02, open=1.04, close=1.07, volume=1000),
            Candle(high=1.12, low=0.98, open=1.07, close=1.09, volume=1000),
        ],
        "direction": Direction.UP,
        "expected_tp": 0.11,
    },
    {
        "name": "4. Multiple candles downtrend",
        "trend_candles": [
            Candle(high=1.05, low=1.00, open=1.04, close=1.01, volume=1000),
            Candle(high=1.02, low=0.98, open=1.01, close=0.99, volume=1000),
            Candle(high=1.01, low=0.92, open=0.99, close=0.96, volume=1000),
        ],
        "direction": Direction.DOWN,
        "expected_tp": 0.12,
    },
    {
        "name": "5. Unknown direction",
        "trend_candles": [
            Candle(high=1.05, low=1.00, open=1.01, close=1.04, volume=1000),
        ],
        "direction": Direction.UNKNOWN,
        "expected_tp": -1,
    },
]


@pytest.mark.parametrize(
    "case", calc_tp_test_cases, ids=[c["name"] for c in calc_tp_test_cases]
)
def test_calc_tp_table_driven(case):
    """
    Тестирование метода calc_tp для расчета Take Profit
    """
    # ARRANGE
    segment = Segment()
    segment.Params = TradeParams(direction=case["direction"])
    segment.Trend = case["trend_candles"]

    # ACT
    segment.calc_tp()

    # ASSERT
    assert round(segment.Params.tp, 2) == round(case["expected_tp"], 2), (
        f"Case: {case['name']} - Expected TP: {case['expected_tp']}, "
        f"but got: {segment.Params.tp}"
    )
