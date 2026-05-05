# tests/test_trade_engine_fsm_flexmock_fn.py
from datetime import datetime
from typing import Any, Dict, List, cast
import logging

import pytest
from flexmock import flexmock

from domain.models.order import Order
from domain.models.TPSL import TPSL
from domain.models.report import Report
from domain.models.trade_unit import Trade_unit
from domain.types.background import Background
from domain.types.power import Power
from domain.types.candle import Candle
from domain.types.candle_action import CandleAction
from domain.types.market_action import MarketAction
from services.bookkeeper.leveraged_bookkeeper import LeveragedBookkeeper
from services.counter_operator.counter_operator import CounterOperatorImpl
from services.history_operator.history_operator import HistoryOperatorImpl
from services.parameters_store.parameters_store import ParametersStoreImpl
from services.plotter.plotter import Plotter
from services.report_operator.report_operator import ReportOperatorImpl
from services.repository.interface import Repository
from services.strategy_operator.strategy_operator_flat import (
    StrategyOperatorFlatImpl,
)
from services.trade_engine.trade_engine_flat import TradeEngineFlat
from services.window_operator.window_operator import WindowOperatorImpl
from services.metric_repository.mock_metric_repository import MockMetricRepository
from services.log_operator.log_operator import LogOperatorImpl

handle_test_cases: List[Dict[str, Any]] = [
    {
        "name": "0. Not_ready -> not_ready",
        "initial_trade_units": [
            Trade_unit(
                candle=Candle(high=97, low=93, open=96, close=94, volume=1000),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(high=96.5, low=94, open=95, close=96, volume=1000),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(high=97, low=93, open=96, close=94, volume=1000),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(high=96.5, low=94, open=95, close=96, volume=1000),
                spread=0.01,
                deposit=1000,
            ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(high=97, low=93, open=96, close=94, volume=1000),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "higher_edge": 100,
        "lower_edge": 99,
        "margin":0.05,
        "expectations": [],
        "expected_higher_edge": 100,
        "expected_lower_edge": 99,
        "expected_states": ["not_ready"],
        "expected_cooldown_counter": 0,
        "expected_history": [],
        "expected_orders": [],
        "expected_TPSL": TPSL(),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.HOLD,
        "expected_desicion_order": Order(),
        "expected_desicion_report": Report(),
    },
    {
        "name": "1. Not_ready -> idle_inside",
        "initial_trade_units": [
            Trade_unit(
                candle=Candle(
                    high=100.5, low=100.4, open=100.45, close=100.48, volume=1000
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.4, low=100.3, open=100.55, close=100.58, volume=1001
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.6, low=100.5, open=100.58, close=100.55, volume=1002
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.6, low=100.5, open=100.55, close=100.58, volume=1003
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.6, low=100.4, open=100.58, close=100.48, volume=1004
                ),
                spread=0.01,
                deposit=1000,
            ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=100.7, low=100.4, open=100.48, close=100.65, volume=1005
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "higher_edge": 101,
        "lower_edge": 100,
        "margin":0.05,
        "expectations": [],
        "expected_higher_edge": 101,
        "expected_lower_edge": 100,
        "expected_states": [
            "not_ready",
            "idle_inside",
        ],
        "expected_cooldown_counter": 0,
        "expected_history": [],
        "expected_orders": [],
        "expected_TPSL": TPSL(),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.HOLD,
        "expected_desicion_order": Order(),
        "expected_desicion_report": Report(),
    },
    {
        "name": "2. Not_ready -> off_market. No entrypoint",
        "initial_trade_units": [
            Trade_unit(
                candle=Candle(
                    high=100.7, low=100.4, open=100.48, close=100.8, volume=1001
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.75, low=100.5, open=100.8, close=100.7, volume=1002
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.75, low=100.6, open=100.7, close=100.68, volume=1003
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.8,
                    low=100.6,
                    open=100.68,
                    close=100.78,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.9,
                    low=100.7,
                    open=100.78,
                    close=100.85,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                spread=0.01,
                deposit=1000,
            ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=101,
                low=100.8,
                open=100.85,
                close=100.95,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 5),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "higher_edge": 101,
        "lower_edge": 100.4,
        "margin":0.05,
        "expectations": [],
        "expected_higher_edge": 101,
        "expected_lower_edge": 100.4,
        "expected_states": [
            "not_ready",
            "idle_inside",
        ],
        "expected_cooldown_counter": 0,
        "expected_history": [],
        "expected_orders": [],
        "expected_TPSL": TPSL(),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.HOLD,
        "expected_desicion_order": Order(),
        "expected_desicion_report": Report(),
    },
    {
        "name": "3. Not_ready -> initial_upper_breakthrough",
        "initial_trade_units": [
            Trade_unit(
                candle=Candle(
                    high=100.6, low=100.5, open=100.55, close=100.78, volume=1002
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.7, low=100.5, open=100.78, close=100.68, volume=1003
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.8,
                    low=100.6,
                    open=100.68,
                    close=100.78,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.9,
                    low=100.7,
                    open=100.78,
                    close=100.85,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101,
                    low=100.8,
                    open=100.85,
                    close=100.95,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                spread=0.01,
                deposit=1000,
            ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=101.2,
                low=100.9,
                open=100.95,
                close=101.1,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 15),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "higher_edge": 101,
        "lower_edge": 100.4,
        "margin":0.05,
        "expectations": [],
        "expected_higher_edge": 101,
        "expected_lower_edge": 100.4,
        "expected_states": [
            "not_ready",
            "initial_upper_breakthrough",
        ],
        "expected_cooldown_counter": 0,
        "expected_history": [
            Candle(
                high=101.2,
                low=100.9,
                open=100.95,
                close=101.1,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 15),
            ),
        ],
        "expected_orders": [
            Order(
                action=CandleAction.SELL,
                entry=101.1,
                volume=3.68,
            ),
        ],
        "expected_TPSL": TPSL(
            volume=3.676,
            sl=101.78,
            tp=100.41,
        ),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.OPEN,
        "expected_desicion_order": Order(
            action=CandleAction.SELL,
            entry=101.1,
            volume=3.676,
        ),
        "expected_decision_TPSL": TPSL(
            volume=3.68,
            sl=101.78,
            tp=100.41,
        ),
        "expected_desicion_report": Report(),
    },
    {
        "name": "4. Not_ready -> initial_upper_breakthrough -> upper_consolidation",
        "initial_trade_units": [
            Trade_unit(
                candle=Candle(
                    high=100.6, low=100.5, open=100.55, close=100.78, volume=1002
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.7, low=100.5, open=100.78, close=100.68, volume=1003
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.8,
                    low=100.6,
                    open=100.68,
                    close=100.78,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.9,
                    low=100.7,
                    open=100.78,
                    close=100.85,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101,
                    low=100.8,
                    open=100.85,
                    close=100.95,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101.2,
                    low=100.9,
                    open=100.95,
                    close=101.1,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 15),
                ),
                spread=0.01,
                deposit=1000,
            ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=101.25,
                low=101.05,
                open=101.1,
                close=101.2,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 20),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "higher_edge": 101,
        "lower_edge": 100.4,
        "margin":0.05,
        "expectations": [],
        "expected_higher_edge": 101,
        "expected_lower_edge": 100.4,
        "expected_states": [
            "not_ready",
            "initial_upper_breakthrough",
            "upper_consolidation",
        ],
        "expected_cooldown_counter": 0,
        "expected_history": [
            Candle(
                high=101.2,
                low=100.9,
                open=100.95,
                close=101.1,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 15),
            ),
            Candle(
                high=101.25,
                low=101.05,
                open=101.1,
                close=101.2,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 20),
            ),
        ],
        "expected_orders": [
            Order(
                action=CandleAction.SELL,
                entry=101.1,
                volume=3.68,
            ),
            Order(
                action=CandleAction.SELL,
                entry=101.25,
                volume=3.68,
            ),
        ],
        "expected_TPSL": TPSL(
            volume=3.676,
            sl=101.78,
            tp=100.41,
        ),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.OPEN,
        "expected_desicion_order": Order(
            action=CandleAction.SELL,
            entry=101.1,
            volume=3.676,
        ),
        "expected_decision_TPSL": TPSL(
            volume=3.68,
            sl=101.78,
            tp=100.41,
        ),
        "expected_desicion_report": Report(),
    },
    {
        "name": "5. Not_ready -> initial_upper_breakthrough -> upper_consolidation -> initial_on_full_on_downtrend. Limit order triggered",
        "initial_trade_units": [
            Trade_unit(
                candle=Candle(
                    high=100.6, low=100.5, open=100.55, close=100.78, volume=1002
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.7, low=100.5, open=100.78, close=100.68, volume=1003
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.8,
                    low=100.6,
                    open=100.68,
                    close=100.78,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.9,
                    low=100.7,
                    open=100.78,
                    close=100.85,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101,
                    low=100.8,
                    open=100.85,
                    close=100.95,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101.2,
                    low=100.9,
                    open=100.95,
                    close=101.1,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 15),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101.25,
                    low=101.05,
                    open=101.1,
                    close=101.2,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 20),
                ),
                spread=0.01,
                deposit=1000,
            ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=101.3,
                low=101.05,
                open=101.2,
                close=101.1,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 25),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "higher_edge": 101,
        "lower_edge": 100.4,
        "margin":0.05,
        "expectations": [],
        "expected_higher_edge": 101,
        "expected_lower_edge": 100.4,
        "expected_states": [
            "not_ready",
            "initial_upper_breakthrough",
            "upper_consolidation",
            "initial_on_full_on_downtrend",
        ],
        "expected_cooldown_counter": 0,
        "expected_history": [
            Candle(
                high=101.2,
                low=100.9,
                open=100.95,
                close=101.1,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 15),
            ),
            Candle(
                high=101.25,
                low=101.05,
                open=101.1,
                close=101.2,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 20),
            ),
            Candle(
                high=101.3,
                low=101.05,
                open=101.2,
                close=101.1,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 25),
            ),
        ],
        "expected_orders": [
            Order(
                action=CandleAction.SELL,
                entry=101.1,
                volume=3.68,
            ),
            Order(
                action=CandleAction.SELL,
                entry=101.25,
                volume=3.68,
            ),
        ],
        "expected_TPSL": TPSL(
            volume=3.676,
            sl=101.78,
            tp=100.41,
        ),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.OPEN,
        "expected_desicion_order": Order(
            action=CandleAction.SELL,
            entry=101.1,
            volume=3.676,
        ),
        "expected_decision_TPSL": TPSL(
            volume=3.68,
            sl=101.78,
            tp=100.41,
        ),
        "expected_desicion_report": Report(),
    },
    {
        "name": "4. Not_ready -> initial_upper_breakthrough -> initial_on_full_off_downtrend. No higher_edge expansion",
        "initial_trade_units": [
            Trade_unit(
                candle=Candle(
                    high=100.6, low=100.5, open=100.55, close=100.78, volume=1002
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.7, low=100.5, open=100.78, close=100.68, volume=1003
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.8,
                    low=100.6,
                    open=100.68,
                    close=100.78,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.9,
                    low=100.7,
                    open=100.78,
                    close=100.85,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101,
                    low=100.8,
                    open=100.85,
                    close=100.95,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
            candle=Candle(
                high=101.1,
                low=100.9,
                open=100.95,
                close=101,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 15),
            ),
            spread=0.01,
            deposit=1000,
        ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=101.2,
                low=100.9,
                open=101,
                close=100.95,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 20),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "higher_edge": 101,
        "lower_edge": 100.4,
        "margin":0.05,
        "expectations": [],
        "expected_higher_edge": 101,
        "expected_lower_edge": 100.4,
        "expected_states": [
            "not_ready",
            "initial_upper_breakthrough",
            "initial_on_full_off_downtrend",
        ],
        "expected_cooldown_counter": 0,
        "expected_history": [
            Candle(
                high=101.1,
                low=100.9,
                open=100.95,
                close=101,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 15),
            ),
            Candle(
                high=101.2,
                low=100.9,
                open=101,
                close=100.95,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 20),
            ),
        ],
        "expected_orders": [
                Order(
                action=CandleAction.SELL,
                entry=101,
                volume=4.31,
            ),
        ],
        "expected_TPSL": TPSL(
            volume=4.31,
            sl=101.58,
            tp=100.41,
        ),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.HOLD,
        "expected_desicion_order": Order(),
        "expected_desicion_report": Report(),
    },
    {
        "name": "5. Not_ready -> initial_upper_breakthrough -> initial_on_full_off_downtrend. Higher_edge expansion",
        "initial_trade_units": [
            Trade_unit(
                candle=Candle(
                    high=100.6, low=100.5, open=100.55, close=100.78, volume=1002
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.7, low=100.5, open=100.78, close=100.68, volume=1003
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.8,
                    low=100.6,
                    open=100.68,
                    close=100.78,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.9,
                    low=100.7,
                    open=100.78,
                    close=100.85,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101,
                    low=100.8,
                    open=100.85,
                    close=100.95,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
            candle=Candle(
                high=101.2,
                low=100.9,
                open=100.95,
                close=101.1,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 15),
            ),
            spread=0.01,
            deposit=1000,
        ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=101.2,
                low=100.9,
                open=101.1,
                close=100.95,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 20),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "higher_edge": 101,
        "lower_edge": 100.4,
        "margin":0.05,
        "expectations": [],
        "expected_higher_edge": 101.1,
        "expected_lower_edge": 100.4,
        "expected_states": [
            "not_ready",
            "initial_upper_breakthrough",
            "initial_on_full_off_downtrend",
        ],
        "expected_cooldown_counter": 0,
        "expected_history": [
            Candle(
                high=101.2,
                low=100.9,
                open=100.95,
                close=101.1,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 15),
            ),
            Candle(
                high=101.2,
                low=100.9,
                open=101.1,
                close=100.95,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 20),
            ),
        ],
        "expected_orders": [
                Order(
                    action=CandleAction.SELL,
                    entry=101.1,
                    volume=3.68,
                ),
        ],
        "expected_TPSL": TPSL(
            volume=3.68,
            sl=101.78,
            tp=100.41,
        ),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.HOLD,
        "expected_desicion_order": Order(),
        "expected_desicion_report": Report(),
    },
    {
        "name": "6. Not_ready -> initial_upper_breakthrough -> initial_on_full_off_downtrend -> cooldown. SL is triggered",
        "initial_trade_units": [
            Trade_unit(
                candle=Candle(
                    high=100.6, low=100.5, open=100.55, close=100.78, volume=1002
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.7, low=100.5, open=100.78, close=100.68, volume=1003
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.8,
                    low=100.6,
                    open=100.68,
                    close=100.78,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.9,
                    low=100.7,
                    open=100.78,
                    close=100.85,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101,
                    low=100.8,
                    open=100.85,
                    close=100.95,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
            candle=Candle(
                high=101.2,
                low=100.9,
                open=100.95,
                close=101.1,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 15),
            ),
            spread=0.01,
            deposit=1000,
        ),
        Trade_unit(
            candle=Candle(
                high=101.2,
                low=100.9,
                open=101.1,
                close=100.95,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 20),
            ),
            spread=0.01,
            deposit=1000,
        ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=101.8,
                low=100.8,
                open=100.95,
                close=100.85,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 25),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "higher_edge": 101,
        "lower_edge": 100.4,
        "margin":0.05,
        "expectations": [],
        "expected_higher_edge": 101.1,
        "expected_lower_edge": 100.4,
        "expected_states": [
            "not_ready",
            "initial_upper_breakthrough",
            "initial_on_full_off_downtrend",
            "cooldown",
        ],
        "expected_cooldown_counter": 4,
        "expected_history": [],
        "expected_orders": [],
        "expected_TPSL": TPSL(),
        "expected_deposit": 997.5,
        "expected_desicion_action": MarketAction.HOLD,
        "expected_desicion_order": Order(),
        "expected_desicion_report": Report(
            candles=[
                    Candle(
                    high=101.2,
                    low=100.9,
                    open=100.95,
                    close=101.1,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 15),
                ),
                Candle(
                    high=101.2,
                    low=100.9,
                    open=101.1,
                    close=100.95,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 20),
                ),
                Candle(
                    high=101.8,
                    low=100.8,
                    open=100.95,
                    close=100.85,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 25),
                ),
            ],
            orders=[
                Order(
                    action=CandleAction.SELL,
                    entry=101.1,
                    volume=3.68,
                ),
            ],
            tpsl=TPSL(
                    volume=3.68,
                    sl=101.78,
                    tp=100.41,
            ),
            reason="Sell_SL",
        ),
    },
    {
        "name": "7. Not_ready -> initial_upper_breakthrough -> initial_on_full_off_downtrend -> subsequent_upper_breakthrough",
        "initial_trade_units": [
            Trade_unit(
                candle=Candle(
                    high=100.6, low=100.5, open=100.55, close=100.78, volume=1002
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.7, low=100.5, open=100.78, close=100.68, volume=1003
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.8,
                    low=100.6,
                    open=100.68,
                    close=100.78,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.9,
                    low=100.7,
                    open=100.78,
                    close=100.85,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101,
                    low=100.8,
                    open=100.85,
                    close=100.95,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101.2,
                    low=100.9,
                    open=100.95,
                    close=101.1,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 15),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101.2,
                    low=100.9,
                    open=101.1,
                    close=100.95,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 20),
                ),
                spread=0.01,
                deposit=1000,
            ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=101.2,
                low=100.9,
                open=100.95,
                close=101.15,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 25),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "higher_edge": 101,
        "lower_edge": 100.4,
        "margin":0.05,
        "expectations": [],
        "expected_higher_edge": 101.1,
        "expected_lower_edge": 100.4,
        "expected_states": [
            "not_ready",
            "initial_upper_breakthrough",
            "initial_on_full_off_downtrend",
            "subsequent_upper_breakthrough",
        ],
        "expected_cooldown_counter": 0,
        "expected_history": [
            Candle(
                high=101.2,
                low=100.9,
                open=100.95,
                close=101.1,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 15),
            ),
            Candle(
                high=101.2,
                low=100.9,
                open=101.1,
                close=100.95,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 20),
            ),
            Candle(
                high=101.2,
                low=100.9,
                open=100.95,
                close=101.15,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 25),
            ),
        ],
        "expected_orders": [
            Order(
                action=CandleAction.SELL,
                entry=101.1,
                volume=3.68,
            ),
        ],
        "expected_TPSL": TPSL(
                volume=3.68,
                sl=101.78,
                tp=100.41,
        ),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.HOLD,
        "expected_desicion_order": Order(),
        "expected_desicion_report": Report(),
    },
    {
        "name": "8. Not_ready -> initial_upper_breakthrough -> initial_on_full_off_downtrend -> subsequent_upper_breakthrough -> initial_on_full_on_downtrend",
        "initial_trade_units": [
            Trade_unit(
                candle=Candle(
                    high=100.6, low=100.5, open=100.55, close=100.78, volume=1002
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.7, low=100.5, open=100.78, close=100.68, volume=1003
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.8,
                    low=100.6,
                    open=100.68,
                    close=100.78,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.9,
                    low=100.7,
                    open=100.78,
                    close=100.85,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101,
                    low=100.8,
                    open=100.85,
                    close=100.95,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101.2,
                    low=100.9,
                    open=100.95,
                    close=101.1,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 15),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101.2,
                    low=100.9,
                    open=101.1,
                    close=100.95,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 20),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101.2,
                    low=100.9,
                    open=100.95,
                    close=101.15,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 25),
                ),
                spread=0.01,
                deposit=1000,
            ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=101.8,
                low=101.05,
                open=101.15,
                close=101.25,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 30),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "higher_edge": 101,
        "lower_edge": 100.4,
        "margin":0.05,
        "expectations": [],
        "expected_higher_edge": 101.1,
        "expected_lower_edge": 100.4,
        "expected_states": [
            "not_ready",
            "initial_upper_breakthrough",
            "initial_on_full_off_downtrend",
            "subsequent_upper_breakthrough",
            "initial_on_full_on_downtrend",
        ],
        "expected_cooldown_counter": 0,
        "expected_history": [
            Candle(
                high=101.2,
                low=100.9,
                open=100.95,
                close=101.1,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 15),
            ),
            Candle(
                high=101.2,
                low=100.9,
                open=101.1,
                close=100.95,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 20),
            ),
            Candle(
                high=101.2,
                low=100.9,
                open=100.95,
                close=101.15,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 25),
            ),
            Candle(
                high=101.8,
                low=101.05,
                open=101.15,
                close=101.25,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 30),
            ),
        ],
        "expected_orders": [
            Order(
                action=CandleAction.SELL,
                entry=101.1,
                volume=3.68,
            ),
            Order(
                action=CandleAction.SELL,
                entry=101.25,
                volume=3.01,
            ),
        ],
        "expected_TPSL": TPSL(
                volume=6.69,
                sl=102.08,
                tp=100.41,
        ),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.HOLD,
        "expected_desicion_order": Order(),
        "expected_desicion_report": Report(),
    },
    {
        "name": "9. Not_ready -> initial_upper_breakthrough -> initial_on_full_off_downtrend -> subsequent_upper_breakthrough -> initial_on_full_on_downtrend. Downtrend candle",
        "initial_trade_units": [
            Trade_unit(
                candle=Candle(
                    high=100.6, low=100.5, open=100.55, close=100.78, volume=1002
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.7, low=100.5, open=100.78, close=100.68, volume=1003
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.8,
                    low=100.6,
                    open=100.68,
                    close=100.78,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.9,
                    low=100.7,
                    open=100.78,
                    close=100.85,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101,
                    low=100.8,
                    open=100.85,
                    close=100.95,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101.2,
                    low=100.9,
                    open=100.95,
                    close=101.1,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 15),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101.2,
                    low=100.9,
                    open=101.1,
                    close=100.95,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 20),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101.2,
                    low=100.9,
                    open=100.95,
                    close=101.15,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 25),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101.3,
                    low=101.05,
                    open=101.15,
                    close=101.25,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 30),
                ),
                spread=0.01,
                deposit=1000,
            ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=101.3,
                low=101.05,
                open=101.25,
                close=101.13,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 35),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "higher_edge": 101,
        "lower_edge": 100.4,
        "margin":0.05,
        "expectations": [],
        "expected_higher_edge": 101.1,
        "expected_lower_edge": 100.4,
        "expected_states": [
            "not_ready",
            "initial_upper_breakthrough",
            "initial_on_full_off_downtrend",
            "subsequent_upper_breakthrough",
            "initial_on_full_on_downtrend",
        ],
        "expected_cooldown_counter": 0,
        "expected_history": [
            Candle(
                high=101.2,
                low=100.9,
                open=100.95,
                close=101.1,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 15),
            ),
            Candle(
                high=101.2,
                low=100.9,
                open=101.1,
                close=100.95,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 20),
            ),
            Candle(
                high=101.2,
                low=100.9,
                open=100.95,
                close=101.15,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 25),
            ),
            Candle(
                high=101.3,
                low=101.05,
                open=101.15,
                close=101.25,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 30),
            ),
            Candle(
                high=101.3,
                low=101.05,
                open=101.25,
                close=101.13,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 35),
            ),
        ],
        "expected_orders": [
            Order(
                action=CandleAction.SELL,
                entry=101.1,
                volume=3.68,
            ),
            Order(
                action=CandleAction.SELL,
                entry=101.25,
                volume=3.01,
            ),
        ],
        "expected_TPSL": TPSL(
                volume=6.69,
                sl=102.08,
                tp=100.41,
        ),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.HOLD,
        "expected_desicion_order": Order(),
        "expected_desicion_report": Report(),
    },
    {
        "name": "10. Not_ready -> initial_upper_breakthrough -> initial_on_full_off_downtrend -> subsequent_upper_breakthrough -> initial_on_full_on_downtrend -> cooldown. SL triggered",
        "initial_trade_units": [
            Trade_unit(
                candle=Candle(
                    high=100.6, low=100.5, open=100.55, close=100.78, volume=1002
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.7, low=100.5, open=100.78, close=100.68, volume=1003
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.8,
                    low=100.6,
                    open=100.68,
                    close=100.78,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.9,
                    low=100.7,
                    open=100.78,
                    close=100.85,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101,
                    low=100.8,
                    open=100.85,
                    close=100.95,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101.2,
                    low=100.9,
                    open=100.95,
                    close=101.1,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 15),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101.2,
                    low=100.9,
                    open=101.1,
                    close=100.95,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 20),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101.2,
                    low=100.9,
                    open=100.95,
                    close=101.15,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 25),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101.3,
                    low=101.05,
                    open=101.15,
                    close=101.25,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 30),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101.3,
                    low=101.05,
                    open=101.25,
                    close=101.13,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 35),
                ),
                spread=0.01,
                deposit=1000,
            ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=102.08,
                low=100.9,
                open=101.13,
                close=101.1,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 40),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "higher_edge": 101,
        "lower_edge": 100.4,
        "margin":0.05,
        "expectations": [],
        "expected_higher_edge": 101.1,
        "expected_lower_edge": 100.4,
        "expected_states": [
            "not_ready",
            "initial_upper_breakthrough",
            "initial_on_full_off_downtrend",
            "subsequent_upper_breakthrough",
            "initial_on_full_on_downtrend",
            "cooldown",
        ],
        "expected_cooldown_counter": 4,
        "expected_history": [],
        "expected_orders": [],
        "expected_TPSL": TPSL(),
        "expected_deposit": 997.5,
        "expected_desicion_action": MarketAction.HOLD,
        "expected_desicion_order": Order(),
        "expected_desicion_report": Report(
            candles=[
                    Candle(
                    high=101.2,
                    low=100.9,
                    open=100.95,
                    close=101.1,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 15),
                ),
                Candle(
                    high=101.2,
                    low=100.9,
                    open=101.1,
                    close=100.95,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 20),
                ),
                Candle(
                    high=101.2,
                    low=100.9,
                    open=100.95,
                    close=101.15,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 25),
                ),
                Candle(
                    high=101.3,
                    low=101.05,
                    open=101.15,
                    close=101.25,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 30),
                ),
                Candle(
                    high=101.3,
                    low=101.05,
                    open=101.25,
                    close=101.13,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 35),
                ),
                Candle(
                    high=102.08,
                    low=100.9,
                    open=101.13,
                    close=101.1,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 40),
                ),
            ],
            orders=[
                Order(
                    action=CandleAction.SELL,
                    entry=101.1,
                    volume=3.68,
                ),
                Order(
                    action=CandleAction.SELL,
                    entry=101.25,
                    volume=3.01,
                ),
            ],
            tpsl=TPSL(
                volume=6.69,
                sl=102.08,
                tp=100.41,
            ),
            reason="Sell_SL",
        ),
    },
    {
        "name": "11. Not_ready -> initial_upper_breakthrough -> initial_on_full_off_downtrend -> subsequent_upper_breakthrough -> initial_on_full_on_downtrend -> cooldown. TP triggered",
        "initial_trade_units": [
            Trade_unit(
                candle=Candle(
                    high=100.6, low=100.5, open=100.55, close=100.78, volume=1002
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.7, low=100.5, open=100.78, close=100.68, volume=1003
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.8,
                    low=100.6,
                    open=100.68,
                    close=100.78,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.9,
                    low=100.7,
                    open=100.78,
                    close=100.85,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101,
                    low=100.8,
                    open=100.85,
                    close=100.95,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101.2,
                    low=100.9,
                    open=100.95,
                    close=101.1,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 15),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101.2,
                    low=100.9,
                    open=101.1,
                    close=100.95,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 20),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101.2,
                    low=100.9,
                    open=100.95,
                    close=101.15,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 25),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101.3,
                    low=101.05,
                    open=101.15,
                    close=101.25,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 30),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101.3,
                    low=101.05,
                    open=101.25,
                    close=101.13,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 35),
                ),
                spread=0.01,
                deposit=1000,
            ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=101.2,
                low=100.4,
                open=101.13,
                close=101.1,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 40),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "higher_edge": 101,
        "lower_edge": 100.4,
        "margin":0.05,
        "expectations": [],
        "expected_higher_edge": 101.1,
        "expected_lower_edge": 100.4,
        "expected_states": [
            "not_ready",
            "initial_upper_breakthrough",
            "initial_on_full_off_downtrend",
            "subsequent_upper_breakthrough",
            "initial_on_full_on_downtrend",
            "cooldown",
        ],
        "expected_cooldown_counter": 4,
        "expected_history": [],
        "expected_orders": [],
        "expected_TPSL": TPSL(),
        "expected_deposit": 1002.53,
        "expected_desicion_action": MarketAction.HOLD,
        "expected_desicion_order": Order(),
        "expected_desicion_report": Report(
            candles=[
                    Candle(
                    high=101.2,
                    low=100.9,
                    open=100.95,
                    close=101.1,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 15),
                ),
                Candle(
                    high=101.2,
                    low=100.9,
                    open=101.1,
                    close=100.95,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 20),
                ),
                Candle(
                    high=101.2,
                    low=100.9,
                    open=100.95,
                    close=101.15,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 25),
                ),
                Candle(
                    high=101.3,
                    low=101.05,
                    open=101.15,
                    close=101.25,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 30),
                ),
                Candle(
                    high=101.3,
                    low=101.05,
                    open=101.25,
                    close=101.13,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 35),
                ),
                Candle(
                    high=101.2,
                    low=100.4,
                    open=101.13,
                    close=101.1,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 40),
                ),
            ],
            orders=[
                Order(
                    action=CandleAction.SELL,
                    entry=101.1,
                    volume=3.68,
                ),
                Order(
                    action=CandleAction.SELL,
                    entry=101.25,
                    volume=3.01,
                ),
            ],
            tpsl=TPSL(
                volume=6.69,
                sl=102.08,
                tp=100.41,
            ),
            reason="Sell_TP",
        ),
    },
    {
        "name": "12. Not_ready -> initial_lower_breakthrough",
        "initial_trade_units": [
            Trade_unit(
                candle=Candle(
                    high=100.6, low=100.5, open=100.55, close=100.78, volume=1002
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.7, low=100.5, open=100.78, close=100.68, volume=1003
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.7,
                    low=100.5,
                    open=100.68,
                    close=100.58,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.6,
                    low=100.4,
                    open=100.58,
                    close=100.45,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.5,
                    low=100.3,
                    open=100.45,
                    close=100.35,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                spread=0.01,
                deposit=1000,
            ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=101.4,
                low=100.2,
                open=100.35,
                close=100.25,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 15),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "higher_edge": 101,
        "lower_edge": 100.3,
        "margin":0.05,
        "expectations": [],
        "expected_higher_edge": 101,
        "expected_lower_edge": 100.3,
        "expected_states": [
            "not_ready",
            "initial_lower_breakthrough",
        ],
        "expected_cooldown_counter": 0,
        "expected_history": [
            Candle(
                high=101.4,
                low=100.2,
                open=100.35,
                close=100.25,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 15),
            ),
        ],
        "expected_orders": [
            Order(
                action=CandleAction.BUY,
                entry=100.25,
                volume=3.42,
            ),
        ],
        "expected_TPSL": TPSL(
            volume=3.42,
            sl=99.52,
            tp=100.99,
        ),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.OPEN,
        "expected_desicion_order": Order(
                action=CandleAction.BUY,
                entry=100.25,
                volume=3.42,
            ),
        "expected_decision_TPSL": TPSL(
            volume=3.42,
            sl=99.52,
            tp=100.99,
        ),
        "expected_desicion_report": Report(),
    },
    {
        "name": "13. Not_ready -> initial_lower_breakthrough -> initial_on_full_off_uptrend. No lower_edge expansion",
        "initial_trade_units": [
            Trade_unit(
                candle=Candle(
                    high=100.6, low=100.5, open=100.55, close=100.78, volume=1002
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.7, low=100.5, open=100.78, close=100.68, volume=1003
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.7,
                    low=100.5,
                    open=100.68,
                    close=100.58,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.6,
                    low=100.4,
                    open=100.58,
                    close=100.45,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.5,
                    low=100.3,
                    open=100.45,
                    close=100.35,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101.4,
                    low=100.2,
                    open=100.35,
                    close=100.3,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 15),
                ),
                spread=0.01,
                deposit=1000,
            ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=101.4,
                low=100.2,
                open=100.3,
                close=100.35,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 25),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "higher_edge": 101,
        "lower_edge": 100.3,
        "margin":0.05,
        "expectations": [],
        "expected_higher_edge": 101,
        "expected_lower_edge": 100.3,
        "expected_states": [
            "not_ready",
            "initial_lower_breakthrough",
            "initial_on_full_off_uptrend",
        ],
        "expected_cooldown_counter": 0,
        "expected_history": [
            Candle(
                high=101.4,
                low=100.2,
                open=100.35,
                close=100.3,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 15),
            ),
            Candle(
                high=101.4,
                low=100.2,
                open=100.3,
                close=100.35,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 25),
            ),
        ],
        "expected_orders": [
            Order(
                action=CandleAction.BUY,
                entry=100.3,
                volume=3.68,
            ),
        ],
        "expected_TPSL": TPSL(
            volume=3.68,
            sl=99.62,
            tp=100.99,
        ),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.HOLD,
        "expected_desicion_order": Order(),
        "expected_decision_TPSL": TPSL(),
        "expected_desicion_report": Report(),
    },
    {
        "name": "14. Not_ready -> initial_lower_breakthrough -> initial_on_full_off_uptrend. Lower_edge expansion",
        "initial_trade_units": [
            Trade_unit(
                candle=Candle(
                    high=100.6, low=100.5, open=100.55, close=100.78, volume=1002
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.7, low=100.5, open=100.78, close=100.68, volume=1003
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.7,
                    low=100.5,
                    open=100.68,
                    close=100.58,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.6,
                    low=100.4,
                    open=100.58,
                    close=100.45,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.5,
                    low=100.3,
                    open=100.45,
                    close=100.35,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101.4,
                    low=100.1,
                    open=100.35,
                    close=100.2,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 15),
                ),
                spread=0.01,
                deposit=1000,
            ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=101.4,
                low=100.1,
                open=100.2,
                close=100.35,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 25),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "higher_edge": 101,
        "lower_edge": 100.3,
        "margin":0.05,
        "expectations": [],
        "expected_higher_edge": 101,
        "expected_lower_edge": 100.2,
        "expected_states": [
            "not_ready",
            "initial_lower_breakthrough",
            "initial_on_full_off_uptrend",
        ],
        "expected_cooldown_counter": 0,
        "expected_history": [
            Candle(
                high=101.4,
                low=100.1,
                open=100.35,
                close=100.2,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 15),
            ),
            Candle(
                high=101.4,
                low=100.1,
                open=100.2,
                close=100.35,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 25),
            ),
        ],
        "expected_orders": [
            Order(
                action=CandleAction.BUY,
                entry=100.2,
                volume=3.21,
            ),
        ],
        "expected_TPSL": TPSL(
            volume=3.21,
            sl=99.42,
            tp=100.99,
        ),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.HOLD,
        "expected_desicion_order": Order(),
        "expected_decision_TPSL": TPSL(),
        "expected_desicion_report": Report(),
    },
]


@pytest.mark.parametrize(
    "case", handle_test_cases, ids=[c["name"] for c in handle_test_cases]
)
def test_trade_engine_flat(case):
    repo = cast(Repository, flexmock())
    plotter = Plotter("data/candles/BTCUSDT/output")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("    - %(levelname)s: [%(engine_id)s] %(message)s")
    console_handler.setFormatter(formatter)

    base_logger = logging.getLogger("")
    base_logger.setLevel(logging.INFO)
    base_logger.addHandler(console_handler)

    logger = logging.LoggerAdapter(base_logger, {"engine_id": "rev_v5"})

    for setup in case.get("expectations", []):
        setup(repo)

    leveraged_bookkeeper = LeveragedBookkeeper(leverage=10)

    strategy_operator_flat = StrategyOperatorFlatImpl(
        bookkeeper=leveraged_bookkeeper,
        metric_repository=MockMetricRepository(),
        logger=logger,
        )

    history_operator = HistoryOperatorImpl()

    window_operator = WindowOperatorImpl(maxlen_window=6)

    counter_operator = CounterOperatorImpl(
        cooldown_counter_max=4,
    )
    report_operator = ReportOperatorImpl()
    parameters_store = ParametersStoreImpl(
        prelude_len=4,
        window_len=6,
        risk_per_full_trade=0.005,
        partial_trade_multiplier=0.5,
        min_price_delta=case["min_price_delta"],
        background=case["background"],
        power=case["power"],
        body_ratio=0.4,
        shadow_ratio=1,
        higher_edge=case["higher_edge"],
        lower_edge=case["lower_edge"],
        margin=case["margin"],
    )

    log_operator = LogOperatorImpl()

    trade_engine_flat = TradeEngineFlat(
        repository=repo,
        bookkeeper=leveraged_bookkeeper,
        strategy_operator=strategy_operator_flat,
        history_operator=history_operator,
        window_operator=window_operator,
        counter_operator=counter_operator,
        report_operator=report_operator,
        log_operator=log_operator,
        parameters_store=parameters_store,
        metric_repository=MockMetricRepository(),
        logger=logger,
    )

    states = []
    num = 0
    for trade_unit in case["initial_trade_units"]:
        output = trade_engine_flat.handle_first(trade_unit)
        if len(output.report.candles) > 0:
            # plotter.plot_full(
            #    candles=output.report.candles,
            #    spread=trade_unit.spread,
            #    order=output.report.order,
            #    folder_name="",
            #    file_name=str(num),
            #    reason=output.report.reason,
            # )
            num += 1
            trade_engine_flat.parameters_store.clear_report()
            trade_engine_flat.parameters_store.orders_reset()

        add(states, cast(str,trade_engine_flat.current_state_value))

    output = trade_engine_flat.handle_first(case["trade_unit"])
    if len(output.report.candles) > 0:
        # plotter.plot_full(
        #    candles=output.report.candles,
        #    spread=case["trade_unit"].spread,
        #    order=output.report.order,
        #    folder_name="",
        #    file_name=str(num),
        #    reason=output.report.reason,
        # )
        trade_engine_flat.parameters_store.clear_report()
        trade_engine_flat.parameters_store.orders_reset()

    add(states, cast(str,trade_engine_flat.current_state_value))

    # Assertions

    assert states == case["expected_states"]

    assert (
        trade_engine_flat.counter_operator.cooldown_counter()
        == case["expected_cooldown_counter"]
    )

    assert trade_engine_flat.history_operator.get() == case["expected_history"]

    for idx,order in enumerate(trade_engine_flat.parameters_store.orders()):
        assert order.action == case["expected_orders"][idx].action
        assert round(order.volume,2) == round(case["expected_orders"][idx].volume,2)
        assert round(order.entry,2) == round(case["expected_orders"][idx].entry,2)


    assert round(trade_engine_flat.parameters_store.tpsl().volume, 2) == round(
        case["expected_TPSL"].volume, 2
    )
    assert round(trade_engine_flat.parameters_store.tpsl().sl, 2) == round(
        case["expected_TPSL"].sl, 2
    )
    assert round(trade_engine_flat.parameters_store.tpsl().tp, 2) == round(
        case["expected_TPSL"].tp, 2
    )

    assert round(trade_engine_flat.parameters_store.deposit(), 2) == round(
        case["expected_deposit"], 2
    ), f"Expected deposit: {case['expected_deposit']}, but got: {trade_engine_flat.parameters_store.deposit()}"

    assert round(trade_engine_flat.parameters_store.higher_edge(), 2) == round(
        case["expected_higher_edge"], 2
    )
    assert round(trade_engine_flat.parameters_store.lower_edge(), 2) == round(
        case["expected_lower_edge"], 2
    )

    assert output.action == case["expected_desicion_action"]

    assert output.order.action == case["expected_desicion_order"].action
    assert round(output.order.entry, 2) == round(
        case["expected_desicion_order"].entry, 2
    )
    assert round(output.order.sl, 2) == round(case["expected_desicion_order"].sl, 2)
    assert round(output.order.tp, 2) == round(case["expected_desicion_order"].tp, 2)
    assert round(output.order.volume, 2) == round(
        case["expected_desicion_order"].volume, 2
    )

    assert output.report.candles == case["expected_desicion_report"].candles

    for idx,order in enumerate(output.report.orders):
        assert order.action == case["expected_desicion_report"].orders[idx].action
        assert round(order.entry, 2) == round(
            case["expected_desicion_report"].orders[idx].entry, 2
        )
        assert round(order.volume, 2) == round(
            case["expected_desicion_report"].orders[idx].volume, 2
        )
    assert round(output.report.tpsl.volume, 2) == round(
        case["expected_desicion_report"].tpsl.volume, 2
    )
    assert round(output.report.tpsl.sl, 2) == round(
        case["expected_desicion_report"].tpsl.sl, 2
    )
    assert round(output.report.tpsl.tp, 2) == round(
        case["expected_desicion_report"].tpsl.tp, 2
    )
    assert output.report.reason == case["expected_desicion_report"].reason


def add(states: List[str], state: str) -> None:
    if len(states) == 0 or (len(states) > 0 and states[-1] != state):
        states.append(state)
        #
        #
