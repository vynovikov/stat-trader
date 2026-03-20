import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest


from domain.models.decision import Decision
from domain.models.order import Order
from domain.models.report import Report
from domain.types.market_action import MarketAction

from services.priority_operator.priority_operator import PriorityOperator

prioritize_counter_test_cases = [
    {
        "name": "0. Both HOLD",
        "decision_primary": Decision(
            engine_id="primary",
            action=MarketAction.HOLD,
            order=Order(),
            report=Report(),
        ),
        "decision_secondary": Decision(
            engine_id="secondary",
            action=MarketAction.HOLD,
            order=Order(),
            report=Report(),
        ),
        "expected_market_action": MarketAction.HOLD,
        "expected_order": Order(),
    },
    {
        "name": "1. Primary HOLD, secondary OPEN",
        "decision_primary": Decision(
            engine_id="primary",
            action=MarketAction.HOLD,
            order=Order(),
            report=Report(),
        ),
        "decision_secondary": Decision(
            engine_id="secondary",
            action=MarketAction.OPEN,
            order=Order(volume=1.1),
            report=Report(),
        ),
        "expected_market_action": MarketAction.OPEN,
        "expected_order": Order(volume=1.1),
    },
    {
        "name": "2. Primary HOLD, secondary CLOSE",
        "decision_primary": Decision(
            engine_id="primary",
            action=MarketAction.HOLD,
            order=Order(),
            report=Report(),
        ),
        "decision_secondary": Decision(
            engine_id="secondary",
            action=MarketAction.CLOSE,
            order=Order(),
            report=Report(),
        ),
        "expected_market_action": MarketAction.CLOSE,
        "expected_order": Order(),
    },
    {
        "name": "3. Primary OPEN, secondary HOLD",
        "decision_primary": Decision(
            engine_id="primary",
            action=MarketAction.OPEN,
            order=Order(),
            report=Report(),
        ),
        "decision_secondary": Decision(
            engine_id="secondary",
            action=MarketAction.HOLD,
            order=Order(),
            report=Report(),
        ),
        "expected_market_action": MarketAction.OPEN,
        "expected_order": Order(),
    },
    {
        "name": "4. Primary OPEN, secondary OPEN",
        "decision_primary": Decision(
            engine_id="primary",
            action=MarketAction.OPEN,
            order=Order(volume=4.1),
            report=Report(),
        ),
        "decision_secondary": Decision(
            engine_id="secondary",
            action=MarketAction.OPEN,
            order=Order(volume=4.2),
            report=Report(),
        ),
        "expected_market_action": MarketAction.OPEN,
        "expected_order": Order(volume=4.1),
    },
    {
        "name": "5. Primary OPEN, secondary CLOSE",
        "decision_primary": Decision(
            engine_id="primary",
            action=MarketAction.OPEN,
            order=Order(volume=5.1),
            report=Report(),
        ),
        "decision_secondary": Decision(
            engine_id="secondary",
            action=MarketAction.CLOSE,
            order=Order(),
            report=Report(),
        ),
        "expected_market_action": MarketAction.CLOSE_THEN_OPEN,
        "expected_order": Order(volume=5.1),
    },
    {
        "name": "6. Primary CLOSE, secondary HOLD",
        "decision_primary": Decision(
            engine_id="primary",
            action=MarketAction.CLOSE,
            order=Order(),
            report=Report(),
        ),
        "decision_secondary": Decision(
            engine_id="secondary",
            action=MarketAction.HOLD,
            order=Order(),
            report=Report(),
        ),
        "expected_market_action": MarketAction.CLOSE,
        "expected_order": Order(),
    },
    {
        "name": "7. Primary CLOSE, secondary OPEN",
        "decision_primary": Decision(
            engine_id="primary",
            action=MarketAction.CLOSE,
            order=Order(volume=4.1),
            report=Report(),
        ),
        "decision_secondary": Decision(
            engine_id="secondary",
            action=MarketAction.OPEN,
            order=Order(volume=4.2),
            report=Report(),
        ),
        "expected_market_action": MarketAction.CLOSE_THEN_OPEN,
        "expected_order": Order(volume=4.2),
    },
    {
        "name": "8. Primary CLOSE, secondary CLOSE",
        "decision_primary": Decision(
            engine_id="primary",
            action=MarketAction.CLOSE,
            order=Order(volume=5.1),
            report=Report(),
        ),
        "decision_secondary": Decision(
            engine_id="secondary",
            action=MarketAction.CLOSE,
            order=Order(),
            report=Report(),
        ),
        "expected_market_action": MarketAction.CLOSE,
        "expected_order": Order(),
    },
]


@pytest.mark.parametrize(
    "case",
    prioritize_counter_test_cases,
    ids=[c["name"] for c in prioritize_counter_test_cases],
)
def test_prioritize_counter(case):
    priority_operator = PriorityOperator()

    got_market_action, got_order, _, _ = priority_operator.prioritize(
        decision_primary=case["decision_primary"],
        decision_secondary=case["decision_secondary"],
    )

    assert (
        got_market_action == case["expected_market_action"]
    ), f"got: {got_market_action}, expected: {case['expected_market_action']}"

    assert (
        got_order == case["expected_order"]
    ), f"got: {got_order}, expected: {case['expected_order']}"
