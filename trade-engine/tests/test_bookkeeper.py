import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from services.bookkeeper.leveraged_bookkeeper import LeveragedBookkeeper
from services.bookkeeper.unleveraged_bookkeeper import UnleveragedBookkeeper

calculate_volume_test_cases_unleveraged = [
    {
        "name": "0. Volume < deposit. Entry_price>SL",
        "entry_price": 100000,
        "sl": 98000,
        "deposit": 1000,
        "risk_per_trade": 0.01,
        "expected_volume": 0.005,
    },
    {
        "name": "1. Volume < deposit. Entry_price<SL",
        "entry_price": 100000,
        "sl": 102000,
        "deposit": 1000,
        "risk_per_trade": 0.01,
        "expected_volume": 0.005,
    },
    {
        "name": "2. Volume > deposit. Entry_price>SL",
        "entry_price": 100000,
        "sl": 99900,
        "deposit": 1000,
        "risk_per_trade": 0.01,
        "expected_volume": 0.1,
    },
    {
        "name": "3. Volume > deposit. Entry_price<SL",
        "entry_price": 100000,
        "sl": 100100,
        "deposit": 1000,
        "risk_per_trade": 0.01,
        "expected_volume": 0.1,
    },
]


@pytest.mark.parametrize(
    "case",
    calculate_volume_test_cases_unleveraged,
    ids=[c["name"] for c in calculate_volume_test_cases_unleveraged],
)
def test_calculate_volume_unleveraged(case):
    volume_operator = UnleveragedBookkeeper()

    volume = volume_operator.calculate_volume(
        case["entry_price"], case["sl"], case["deposit"], case["risk_per_trade"]
    )

    assert (
        volume == case["expected_volume"]
    ), f"expected {case["expected_volume"]}, got {volume}"


calculate_volume_test_cases_leveraged = [
    {
        "name": "0. Volume < min_volume. Entry_price>SL",
        "entry_price": 100000,
        "sl": 98000,
        "deposit": 1000,
        "risk_per_trade": 0.01,
        "min_volume": 0.02,
        "safety_factpr": 0.15,
        "expected_volume": 0.02,
    },
    {
        "name": "1. min_volume < volume < max_volume. Entry_price>SL",
        "entry_price": 100000,
        "sl": 99500,
        "deposit": 8000,
        "risk_per_trade": 0.01,
        "min_volume": 0.02,
        "safety_factpr": 0.15,
        "expected_volume": 0.08,
    },
    {
        "name": "2. volume > max_volume. Entry_price>SL",
        "entry_price": 100000,
        "sl": 99900,
        "deposit": 10000,
        "risk_per_trade": 0.01,
        "min_volume": 0.02,
        "safety_factor": 0.15,
        "expected_volume": 0.1,
    },
]


@pytest.mark.parametrize(
    "case",
    calculate_volume_test_cases_leveraged,
    ids=[c["name"] for c in calculate_volume_test_cases_leveraged],
)
def test_calculate_volume_leveraged(case):
    volume_operator = LeveragedBookkeeper(leverage=2)

    volume = volume_operator.calculate_volume(
        entry_price=case["entry_price"],
        sl=case["sl"],
        deposit=case["deposit"],
        risk_per_trade=case["risk_per_trade"],
        min_volume=case["min_volume"],
    )

    assert (
        volume == case["expected_volume"]
    ), f"expected {case["expected_volume"]}, got {volume}"


profit_test_cases_unleveraged = [
    {
        "name": "0. Price difference >0",
        "price_difference": 100,
        "volume": 0.05,
        "expected_profit": 5.0,
    },
    {
        "name": "1. Price difference <0",
        "price_difference": -89,
        "volume": 0.05,
        "expected_profit": -4.45,
    },
]


@pytest.mark.parametrize(
    "case",
    profit_test_cases_unleveraged,
    ids=[c["name"] for c in profit_test_cases_unleveraged],
)
def test_profit_unleveraged(case):
    volume_operator = UnleveragedBookkeeper()

    profit = volume_operator.profit(case["price_difference"], case["volume"])

    assert (
        profit == case["expected_profit"]
    ), f"expected {case["expected_profit"]}, got {profit}"


profit_test_cases_leveraged = [
    {
        "name": "0. Price difference >0",
        "price_difference": 100,
        "volume": 0.05,
        "expected_profit": 5,
    },
    {
        "name": "1. Price difference <0",
        "price_difference": -89,
        "volume": 0.05,
        "expected_profit": -4.45,
    },
]


@pytest.mark.parametrize(
    "case",
    profit_test_cases_leveraged,
    ids=[c["name"] for c in profit_test_cases_leveraged],
)
def test_profit_leveraged(case):
    volume_operator = LeveragedBookkeeper(leverage=2)
    profit = volume_operator.profit(case["price_difference"], case["volume"])

    assert (
        profit == case["expected_profit"]
    ), f"expected {case["expected_profit"]}, got {profit}"
