from typing import Any, Dict, List
import pytest

from domain.models.decision import Decision
from domain.models.order import Order
from domain.models.report import Report
from domain.models.TPSL import TPSL
from domain.types.market_action import MarketAction

from services.usecases.usecases_multi_engine import UsecasesMultiEngine
from services.metric_repository.mock_metric_repository import MockMetricRepository

_get_decision_test_cases: List[Dict[str, Any]] = [
    {
        "name":"0. All actions = MarketAction.HOLD",
        "engage_engine_id":"",
        "decisions":[
            Decision(
            engine_id="rev_v5",
            order=Order(),
            tpsl=TPSL(),
            action=MarketAction.HOLD,
            report=Report(),
        ),
        Decision(
            engine_id="con_v6",
            order=Order(),
            tpsl=TPSL(),
            action=MarketAction.HOLD,
            report=Report(),
        ),
        ],
        "expected_decision":
            Decision(
                engine_id="",
                order=Order(),
                tpsl=TPSL(),
                action=MarketAction.HOLD,
                report=Report(),
            ),
        "expected_engage_engine_id": "",
    },
    {
        "name":"1. One action = MarketAction.OPEN. Engage_engine_id is empty",
        "engage_engine_id":"",
        "decisions":[
            Decision(
                engine_id="rev_v5",
                order=Order(),
                tpsl=TPSL(),
                action=MarketAction.OPEN,
                report=Report(),
            ),
            Decision(
                engine_id="con_v6",
                order=Order(),
                tpsl=TPSL(),
                action=MarketAction.HOLD,
                report=Report(),
            ),
        ],
        "expected_decision":
            Decision(
                engine_id="rev_v5",
                order=Order(),
                tpsl=TPSL(),
                action=MarketAction.OPEN,
                report=Report(),
            ),
        "expected_engage_engine_id": "rev_v5",
    },
    {
        "name":"2. One action = MarketAction.OPEN. Engage_engine_id is not empty",
        "engage_engine_id":"con_v6",
        "decisions":[
            Decision(
            engine_id="rev_v5",
            order=Order(),
            tpsl=TPSL(),
            action=MarketAction.OPEN,
            report=Report(),
        ),
        Decision(
            engine_id="con_v6",
            order=Order(),
            tpsl=TPSL(),
            action=MarketAction.HOLD,
            report=Report(),
        ),
        ],
        "expected_decision":
            Decision(
                engine_id="",
                order=Order(),
                tpsl=TPSL(),
                action=MarketAction.HOLD,
                report=Report(),
            ),
        "expected_engage_engine_id": "con_v6",
    },
    {
        "name":"3. One action = MarketAction.CLOSE. Engage_engine_id == decision.engine_id",
        "engage_engine_id":"rev_v5",
        "decisions":[
            Decision(
                engine_id="rev_v5",
                order=Order(),
                tpsl=TPSL(),
                action=MarketAction.CLOSE,
                report=Report(),
            ),
            Decision(
                engine_id="con_v6",
                order=Order(),
                tpsl=TPSL(),
                action=MarketAction.HOLD,
                report=Report(),
            ),
        ],
        "expected_decision":
            Decision(
                engine_id="rev_v5",
                order=Order(),
                tpsl=TPSL(),
                action=MarketAction.CLOSE,
                report=Report(),
            ),
        "expected_engage_engine_id": "",
    },
    {
        "name":"4. One action = MarketAction.CLOSE. Engage_engine_id != decision.engine_id",
        "engage_engine_id":"con_v6",
        "decisions":[
            Decision(
                engine_id="rev_v5",
                order=Order(),
                tpsl=TPSL(),
                action=MarketAction.CLOSE,
                report=Report(),
            ),
            Decision(
                engine_id="con_v6",
                order=Order(),
                tpsl=TPSL(),
                action=MarketAction.HOLD,
                report=Report(),
            ),
        ],
        "expected_decision":
            Decision(
                engine_id="",
                order=Order(),
                tpsl=TPSL(),
                action=MarketAction.HOLD,
                report=Report(),
            ),
        "expected_engage_engine_id": "con_v6",
    },
]

@pytest.mark.parametrize(
    "case", _get_decision_test_cases, ids=[c["name"] for c in _get_decision_test_cases]
)
def test_strategy_operator_entrypoint(case):
    usecases=UsecasesMultiEngine(
        trade_engines=[],
        metric_repository=MockMetricRepository(),
        engage_engine_id=case["engage_engine_id"],
    )

    decision=usecases._get_decision(case["decisions"])

    assert (
        decision == case["expected_decision"]
    ), f"expected_decision {case["expected_decision"]} but got {decision}"

    assert (
        usecases.engage_engine_id == case["expected_engage_engine_id"]
    ), f"expected_engage_engine_id {case["expected_engage_engine_id"]} but got {usecases.engage_engine_id}"
