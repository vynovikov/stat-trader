# tests/test_trade_engine_fsm_flexmock_fn.py
from datetime import datetime
from typing import Any, Dict, List, cast
import logging

import pytest
from flexmock import flexmock

from domain.models.order import Order
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
        "expected_order": Order(
            action=CandleAction.NONE, entry=0, sl=0, tp=0, volume=0
        ),
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
        "expected_order": Order(
            action=CandleAction.NONE, entry=0, sl=0, tp=0, volume=0
        ),
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
        "expected_order": Order(),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.HOLD,
        "expected_desicion_order": Order(),
        "expected_desicion_report": Report(),
    },
    {
        "name": "3.0 Not_ready -> initial_upper_breakthrough. Sell entrypoint. Pattern [UP]. Candle.high > higher_edge",
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
        "expected_order": Order(
            action=CandleAction.SELL,
            entry=101.12,
            sl=101.49,
            tp=100.39,
            volume=6.33,
        ),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.OPEN,
        "expected_desicion_order": Order(
            action=CandleAction.SELL,
            entry=101.12,
            sl=101.49,
            tp=100.39,
            volume=6.33,
        ),
        "expected_desicion_report": Report(),
    },
    {
        "name": "3.1 Not_ready -> initial_upper_breakthrough. Sell entrypoint. Pattern [DOWN]. Candle.high > higher_edge",
        "initial_trade_units": [
            Trade_unit(
                candle=Candle(
                    high=100.6, low=100.5, open=100.55, close=100.68, volume=1002
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.7, low=100.5, open=100.68, close=100.78, volume=1003
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.8,
                    low=100.6,
                    open=100.78,
                    close=100.73,
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
                    open=100.73,
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
                    close=100.99,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                spread=0.01,
                deposit=1000,
            ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=101.05,
                low=100.9,
                open=100.99,
                close=100.98,
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
                high=101.05,
                low=100.9,
                open=100.99,
                close=100.98,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 15),
            ),
        ],
        "expected_order": Order(
            action=CandleAction.SELL,
            entry=101,
            sl=101.32,
            tp=100.39,
            volume=7.46,
        ),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.OPEN,
        "expected_desicion_order": Order(
            action=CandleAction.SELL,
            entry=101,
            sl=101.32,
            tp=100.39,
            volume=7.46,
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
        "expected_order": Order(
            action=CandleAction.SELL,
            entry=101.02,
            sl=101.34,
            tp=100.39,
            volume=7.25,
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
        "expected_order": Order(
            action=CandleAction.SELL,
            entry=101.12,
            sl=101.49,
            tp=100.39,
            volume=6.33,
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
                high=101.5,
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
        "expected_history": [ ],
        "expected_order": Order(),
        "expected_deposit": 997.63,
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
                high=101.5,
                low=100.8,
                open=100.95,
                close=100.85,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 25),
            ),
            ],
            order=Order(
                action=CandleAction.SELL,
                entry=101.12,
                sl=101.49,
                tp=100.39,
                volume=6.33,
            ),
            reason="Sell_SL",
        ),
    },
    {
        "name": "6. Not_ready -> on_market_downtrend. Entry is triggered",
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
                low=100.97,
                open=101.1,
                close=101.15,
                volume=1006,
                close_time=datetime(2025, 1, 1, 0, 20),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "expectations": [],
        "expected_states": [
            "not_ready",
            "orders_downtrend",
            "on_market_downtrend",
        ],
        "expected_cooldown_counter": 0,
        "expected_history": [
            Candle(high=100.7, low=100.5, open=100.78, close=100.68, volume=1003),
            Candle(
                high=100.8,
                low=100.6,
                open=100.68,
                close=100.78,
                volume=1004,
                close_time=datetime(2025, 1, 1, 0, 0),
            ),
            Candle(
                high=100.9,
                low=100.7,
                open=100.78,
                close=100.85,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 5),
            ),
            Candle(
                high=101,
                low=100.8,
                open=100.85,
                close=100.95,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 10),
            ),
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
                low=100.97,
                open=101.1,
                close=101.15,
                volume=1006,
                close_time=datetime(2025, 1, 1, 0, 20),
            ),
        ],
        "expected_order": Order(
            action=CandleAction.SELL,
            entry=101.12,
            sl=101.48,
            tp=100.42,
            volume=13.16,
        ),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.HOLD,
        "expected_desicion_order": Order(),
        "expected_desicion_report": Report(),
    },
    {
        "name": "7. Not_ready -> on_market_downtrend. Entry and SL is triggered",
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
                high=101.48,
                low=101.08,
                open=101.1,
                close=101.25,
                volume=1006,
                close_time=datetime(2025, 1, 1, 0, 20),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "expectations": [],
        "expected_states": [
            "not_ready",
            "orders_downtrend",
            "cooldown",
        ],
        "expected_cooldown_counter": 3,
        "expected_history": [],
        "expected_order": Order(),
        "expected_deposit": 995.26,
        "expected_desicion_action": MarketAction.CLOSE,
        "expected_desicion_order": Order(),
        "expected_desicion_report": Report(
            candles=[
                Candle(high=100.7, low=100.5, open=100.78, close=100.68, volume=1003),
                Candle(
                    high=100.8,
                    low=100.6,
                    open=100.68,
                    close=100.78,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                Candle(
                    high=100.9,
                    low=100.7,
                    open=100.78,
                    close=100.85,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                Candle(
                    high=101,
                    low=100.8,
                    open=100.85,
                    close=100.95,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                Candle(
                    high=101.2,
                    low=100.9,
                    open=100.95,
                    close=101.1,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 15),
                ),
                Candle(
                high=101.48,
                low=101.08,
                open=101.1,
                close=101.25,
                volume=1006,
                close_time=datetime(2025, 1, 1, 0, 20),
            ),
            ],
            order=Order(
            action=CandleAction.SELL,
            entry=101.12,
            sl=101.48,
            tp=100.42,
            volume=13.16,
        ),
            reason="Sell_SL",
        ),
    },
    {
        "name": "8. Not_ready -> on_market_downtrend. Candles continue uptrend. SL is not triggered",
        "initial_trade_units": [
            Trade_unit(
                candle=Candle(
                    high=100.8, low=100.5, open=100.55, close=100.7, volume=1002
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.7, low=100.6, open=100.7, close=100.68, volume=1003
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
                    volume=1006,
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
                    volume=1007,
                    close_time=datetime(2025, 1, 1, 0, 15),
                ),
                spread=0.01,
                deposit=1000,
            ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=101.27,
                low=101.05,
                open=101.1,
                close=101.23,
                volume=1007,
                close_time=datetime(2025, 1, 1, 0, 20),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "expectations": [],
        "expected_states": [
            "not_ready",
            "orders_downtrend",
            "on_market_downtrend",
        ],
        "expected_cooldown_counter": 0,
        "expected_history": [
            Candle(high=100.7, low=100.6, open=100.7, close=100.68, volume=1003),
            Candle(
                high=100.8,
                low=100.6,
                open=100.68,
                close=100.78,
                volume=1004,
                close_time=datetime(2025, 1, 1, 0, 0),
            ),
            Candle(
                high=100.9,
                low=100.7,
                open=100.78,
                close=100.85,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 5),
            ),
            Candle(
                high=101,
                low=100.8,
                open=100.85,
                close=100.95,
                volume=1006,
                close_time=datetime(2025, 1, 1, 0, 10),
            ),
            Candle(
                high=101.2,
                low=100.9,
                open=100.95,
                close=101.1,
                volume=1007,
                close_time=datetime(2025, 1, 1, 0, 15),
            ),
            Candle(
                high=101.27,
                low=101.05,
                open=101.1,
                close=101.23,
                volume=1007,
                close_time=datetime(2025, 1, 1, 0, 20),
            ),
        ],
        "expected_order": Order(
            action=CandleAction.SELL,
            entry=101.12,
            sl=101.43,
            tp=100.52,
            volume=15.15,
        ),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.HOLD,
        "expected_desicion_order": Order(),
        "expected_desicion_report": Report(),
    },
    {
        "name": "9. Not_ready -> orders_downtrend -> on_market_downtrend -> cooldown. Candle triggers SL",
        "initial_trade_units": [
            Trade_unit(
                candle=Candle(
                    high=100.8, low=100.5, open=100.55, close=100.7, volume=1002
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.7, low=100.6, open=100.7, close=100.68, volume=1003
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
                    volume=1006,
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
                    volume=1007,
                    close_time=datetime(2025, 1, 1, 0, 15),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=101.27,
                    low=101.05,
                    open=101.1,
                    close=101.23,
                    volume=1008,
                    close_time=datetime(2025, 1, 1, 0, 20),
                ),
                spread=0.01,
                deposit=1000,
            ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=101.43,
                low=101.18,
                open=101.23,
                close=101.32,
                volume=1009,
                close_time=datetime(2025, 1, 1, 0, 25),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "expectations": [],
        "expected_states": [
            "not_ready",
            "orders_downtrend",
            "on_market_downtrend",
            "cooldown",
        ],
        "expected_cooldown_counter": 3,
        "expected_history": [],
        "expected_order": Order(),
        "expected_deposit": 995.3,
        "expected_desicion_action": MarketAction.CLOSE,
        "expected_desicion_order": Order(),
        "expected_desicion_report": Report(
            candles=[
                Candle(high=100.7, low=100.6, open=100.7, close=100.68, volume=1003),
                Candle(
                    high=100.8,
                    low=100.6,
                    open=100.68,
                    close=100.78,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                Candle(
                    high=100.9,
                    low=100.7,
                    open=100.78,
                    close=100.85,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                Candle(
                    high=101,
                    low=100.8,
                    open=100.85,
                    close=100.95,
                    volume=1006,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                Candle(
                    high=101.2,
                    low=100.9,
                    open=100.95,
                    close=101.1,
                    volume=1007,
                    close_time=datetime(2025, 1, 1, 0, 15),
                ),
                Candle(
                    high=101.27,
                    low=101.05,
                    open=101.1,
                    close=101.23,
                    volume=1008,
                    close_time=datetime(2025, 1, 1, 0, 20),
                ),
                Candle(
                    high=101.43,
                    low=101.18,
                    open=101.23,
                    close=101.32,
                    volume=1009,
                    close_time=datetime(2025, 1, 1, 0, 25),
                ),
            ],
            order=Order(
                action=CandleAction.SELL,
                entry=101.12,
                sl=101.43,
                tp=100.52,
                volume=15.15,
            ),
            reason="Sell_SL",
        ),
    },
    {
        "name": "10.0. Not_ready -> orders_uptrend. 5 trend candles. Pattern [UP DOWN DOWN DOWN DOWN]. Background is FLAT_REV",
        "initial_trade_units": [
            Trade_unit(
                candle=Candle(
                    high=100.6, low=100.5, open=100.55, close=100.58, volume=1002
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.7, low=100.5, open=100.58, close=100.68, volume=1003
                ),
                spread=0.01,
                deposit=1001,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.75,
                    low=100.5,
                    open=100.68,
                    close=100.58,
                    volume=1002,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.65,
                    low=100.4,
                    open=100.58,
                    close=100.48,
                    volume=1003,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.55,
                    low=100.3,
                    open=100.48,
                    close=100.38,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                spread=0.01,
                deposit=1000,
            ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=100.45,
                low=100.2,
                open=100.38,
                close=100.28,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 15),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "expectations": [],
        "expected_states": [
            "not_ready",
            "orders_uptrend",
        ],
        "expected_cooldown_counter": 0,
        "expected_history": [
            Candle(high=100.7, low=100.5, open=100.58, close=100.68, volume=1003),
            Candle(
                high=100.75,
                low=100.5,
                open=100.68,
                close=100.58,
                volume=1002,
                close_time=datetime(2025, 1, 1, 0, 0),
            ),
            Candle(
                high=100.65,
                low=100.4,
                open=100.58,
                close=100.48,
                volume=1003,
                close_time=datetime(2025, 1, 1, 0, 5),
            ),
            Candle(
                high=100.55,
                low=100.3,
                open=100.48,
                close=100.38,
                volume=1004,
                close_time=datetime(2025, 1, 1, 0, 10),
            ),
            Candle(
                high=100.45,
                low=100.2,
                open=100.38,
                close=100.28,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 15),
            ),
        ],
        "expected_order": Order(
            action=CandleAction.BUY,
            entry=100.26,
            sl=99.98,
            tp=100.81,
            volume=16.39,
        ),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.OPEN,
        "expected_desicion_order": Order(
            action=CandleAction.BUY,
            entry=100.26,
            sl=99.98,
            tp=100.81,
            volume=16.39,
        ),
        "expected_desicion_report": Report(),
    },
    {
        "name": "10.1. Not_ready -> orders_uptrend. 5 trend candles. Pattern [DOWN UP DOWN DOWN DOWN]. Background is FLAT_REV",
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
                deposit=1001,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.75,
                    low=100.5,
                    open=100.68,
                    close=100.71,
                    volume=1002,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.75,
                    low=100.4,
                    open=100.71,
                    close=100.48,
                    volume=1003,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.55,
                    low=100.3,
                    open=100.48,
                    close=100.38,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                spread=0.01,
                deposit=1000,
            ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=100.45,
                low=100.2,
                open=100.38,
                close=100.28,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 15),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "expectations": [],
        "expected_states": [
            "not_ready",
            "orders_uptrend",
        ],
        "expected_cooldown_counter": 0,
        "expected_history": [
            Candle(
                    high=100.7, low=100.5, open=100.78, close=100.68, volume=1003
                ),
            Candle(
                    high=100.75,
                    low=100.5,
                    open=100.68,
                    close=100.71,
                    volume=1002,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
            Candle(
                    high=100.75,
                    low=100.4,
                    open=100.71,
                    close=100.48,
                    volume=1003,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
            Candle(
                    high=100.55,
                    low=100.3,
                    open=100.48,
                    close=100.38,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
            Candle(
                high=100.45,
                low=100.2,
                open=100.38,
                close=100.28,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 15),
            ),
        ],
        "expected_order": Order(
            action=CandleAction.BUY,
            entry=100.26,
            sl=99.98,
            tp=100.81,
            volume=16.39,
        ),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.OPEN,
        "expected_desicion_order": Order(
            action=CandleAction.BUY,
            entry=100.26,
            sl=99.98,
            tp=100.81,
            volume=16.39,
        ),
        "expected_desicion_report": Report(),
    },
    {
        "name": "10.2. Not_ready -> orders_uptrend. 5 trend candles. Pattern [DOWN DOWN UP DOWN DOWN]. Background is FLAT_REV",
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
                deposit=1001,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.75,
                    low=100.5,
                    open=100.68,
                    close=100.58,
                    volume=1002,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.65,
                    low=100.55,
                    open=100.58,
                    close=100.61,
                    volume=1003,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.65,
                    low=100.3,
                    open=100.61,
                    close=100.38,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                spread=0.01,
                deposit=1000,
            ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=100.45,
                low=100.2,
                open=100.38,
                close=100.28,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 15),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "expectations": [],
        "expected_states": [
            "not_ready",
            "orders_uptrend",
        ],
        "expected_cooldown_counter": 0,
        "expected_history": [
            Candle(high=100.7, low=100.5, open=100.78, close=100.68, volume=1003),
            Candle(
                high=100.75,
                low=100.5,
                open=100.68,
                close=100.58,
                volume=1002,
                close_time=datetime(2025, 1, 1, 0, 0),
            ),
            Candle(
                high=100.65,
                low=100.55,
                open=100.58,
                close=100.61,
                volume=1003,
                close_time=datetime(2025, 1, 1, 0, 5),
            ),
            Candle(
                high=100.65,
                low=100.3,
                open=100.61,
                close=100.38,
                volume=1004,
                close_time=datetime(2025, 1, 1, 0, 10),
            ),
            Candle(
                high=100.45,
                low=100.2,
                open=100.38,
                close=100.28,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 15),
            ),
        ],
        "expected_order": Order(
            action=CandleAction.BUY,
            entry=100.26,
            sl=99.98,
            tp=100.81,
            volume=16.39,
        ),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.OPEN,
        "expected_desicion_order": Order(
            action=CandleAction.BUY,
            entry=100.26,
            sl=99.98,
            tp=100.81,
            volume=16.39,
        ),
        "expected_desicion_report": Report(),
    },
    {
        "name": "10.3. Not_ready -> orders_uptrend. 5 trend candles. Pattern [DOWN DOWN UP DOWN DOWN]. Background is FLAT_REV",
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
                deposit=1001,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.75,
                    low=100.5,
                    open=100.68,
                    close=100.58,
                    volume=1002,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.65,
                    low=100.55,
                    open=100.58,
                    close=100.61,
                    volume=1003,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.65,
                    low=100.3,
                    open=100.61,
                    close=100.38,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                spread=0.01,
                deposit=1000,
            ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=100.45,
                low=100.2,
                open=100.38,
                close=100.28,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 15),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "expectations": [],
        "expected_states": [
            "not_ready",
            "orders_uptrend",
        ],
        "expected_cooldown_counter": 0,
        "expected_history": [
            Candle(high=100.7, low=100.5, open=100.78, close=100.68, volume=1003),
            Candle(
                high=100.75,
                low=100.5,
                open=100.68,
                close=100.58,
                volume=1002,
                close_time=datetime(2025, 1, 1, 0, 0),
            ),
            Candle(
                high=100.65,
                low=100.55,
                open=100.58,
                close=100.61,
                volume=1003,
                close_time=datetime(2025, 1, 1, 0, 5),
            ),
            Candle(
                high=100.65,
                low=100.3,
                open=100.61,
                close=100.38,
                volume=1004,
                close_time=datetime(2025, 1, 1, 0, 10),
            ),
            Candle(
                high=100.45,
                low=100.2,
                open=100.38,
                close=100.28,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 15),
            ),
        ],
        "expected_order": Order(
            action=CandleAction.BUY,
            entry=100.26,
            sl=99.98,
            tp=100.81,
            volume=16.39,
        ),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.OPEN,
        "expected_desicion_order": Order(
            action=CandleAction.BUY,
            entry=100.26,
            sl=99.98,
            tp=100.81,
            volume=16.39,
        ),
        "expected_desicion_report": Report(),
    },
    {
        "name": "10.4. Not_ready -> orders_uptrend. 5 trend candles. Pattern [DOWN DOWN DOWN UP DOWN]. Background is FLAT_REV",
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
                deposit=1001,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.75,
                    low=100.5,
                    open=100.68,
                    close=100.58,
                    volume=1002,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.65,
                    low=100.55,
                    open=100.58,
                    close=100.48,
                    volume=1003,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.55,
                    low=100.45,
                    open=100.48,
                    close=100.51,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                spread=0.01,
                deposit=1000,
            ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=100.45,
                low=100.2,
                open=100.51,
                close=100.28,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 15),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "expectations": [],
        "expected_states": [
            "not_ready",
            "orders_uptrend",
        ],
        "expected_cooldown_counter": 0,
        "expected_history": [
            Candle(high=100.7, low=100.5, open=100.78, close=100.68, volume=1003),
            Candle(
                high=100.75,
                low=100.5,
                open=100.68,
                close=100.58,
                volume=1002,
                close_time=datetime(2025, 1, 1, 0, 0),
            ),
            Candle(
                high=100.65,
                low=100.55,
                open=100.58,
                close=100.48,
                volume=1003,
                close_time=datetime(2025, 1, 1, 0, 5),
            ),
            Candle(
                high=100.55,
                low=100.45,
                open=100.48,
                close=100.51,
                volume=1004,
                close_time=datetime(2025, 1, 1, 0, 10),
            ),
            Candle(
                high=100.45,
                low=100.2,
                open=100.51,
                close=100.28,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 15),
            ),
        ],
        "expected_order": Order(
            action=CandleAction.BUY,
            entry=100.26,
            sl=99.98,
            tp=100.81,
            volume=16.39,
        ),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.OPEN,
        "expected_desicion_order": Order(
            action=CandleAction.BUY,
            entry=100.26,
            sl=99.98,
            tp=100.81,
            volume=16.39,
        ),
        "expected_desicion_report": Report(),
    },
    {
        "name": "11. Not_ready -> orders_uptrend. 5 trend candles. Background is SELL_TREND",
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
                deposit=1001,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.75,
                    low=100.5,
                    open=100.68,
                    close=100.58,
                    volume=1002,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.65,
                    low=100.4,
                    open=100.58,
                    close=100.48,
                    volume=1003,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.55,
                    low=100.3,
                    open=100.48,
                    close=100.38,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                spread=0.01,
                deposit=1000,
            ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=100.45,
                low=100.2,
                open=100.38,
                close=100.28,
                volume=1005,
                close_time=datetime(2025, 1, 1, 0, 15),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.BEARISH_REV,
        "power": Power.WEAK,
        "expectations": [],
        "expected_states": [
            "not_ready",
            "idle",
        ],
        "expected_cooldown_counter": 0,
        "expected_history": [],
        "expected_order": Order(),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.HOLD,
        "expected_desicion_order": Order(),
        "expected_desicion_report": Report(),
    },
    {
        "name": "12. Not_ready -> on_market_uptrend. Entry triggered",
        "initial_trade_units": [
            Trade_unit(
                candle=Candle(
                    high=100.6, low=100.5, open=100.55, close=100.65, volume=1002
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.7, low=100.5, open=100.65, close=100.68, volume=1003
                ),
                spread=0.01,
                deposit=1001,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.75,
                    low=100.5,
                    open=100.68,
                    close=100.58,
                    volume=1002,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.65,
                    low=100.4,
                    open=100.58,
                    close=100.48,
                    volume=1003,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.55,
                    low=100.3,
                    open=100.48,
                    close=100.38,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.45,
                    low=100.2,
                    open=100.38,
                    close=100.28,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 15),
                ),
                spread=0.01,
                deposit=1000,
            ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=100.33,
                low=100.19,
                open=100.28,
                close=100.21,
                volume=1006,
                close_time=datetime(2025, 1, 1, 0, 20),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "expectations": [],
        "expected_states": [
            "not_ready",
            "orders_uptrend",
            "on_market_uptrend",
        ],
        "expected_cooldown_counter": 0,
        "expected_history": [
            Candle(high=100.7, low=100.5, open=100.65, close=100.68, volume=1003),
                Candle(
                    high=100.75,
                    low=100.5,
                    open=100.68,
                    close=100.58,
                    volume=1002,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                Candle(
                    high=100.65,
                    low=100.4,
                    open=100.58,
                    close=100.48,
                    volume=1003,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                Candle(
                    high=100.55,
                    low=100.3,
                    open=100.48,
                    close=100.38,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                Candle(
                    high=100.45,
                    low=100.2,
                    open=100.38,
                    close=100.28,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 15),
                ),
                Candle(
                    high=100.33,
                    low=100.19,
                    open=100.28,
                    close=100.21,
                    volume=1006,
                    close_time=datetime(2025, 1, 1, 0, 20),
                ),
        ],
        "expected_order": Order(
            action=CandleAction.BUY,
            entry=100.26,
            sl=99.98,
            tp=100.81,
            volume=16.39,
        ),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.HOLD,
        "expected_desicion_order": Order(),
        "expected_desicion_report": Report( ),
    },
    {
        "name": "13. Not_ready -> orders_uptrend -> cooldown. Entry and SL triggered",
        "initial_trade_units": [
            Trade_unit(
                candle=Candle(
                    high=100.6, low=100.5, open=100.55, close=100.58, volume=1002
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.7, low=100.5, open=100.58, close=100.68, volume=1003
                ),
                spread=0.01,
                deposit=1001,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.75,
                    low=100.5,
                    open=100.68,
                    close=100.58,
                    volume=1002,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.65,
                    low=100.4,
                    open=100.58,
                    close=100.48,
                    volume=1003,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.55,
                    low=100.3,
                    open=100.48,
                    close=100.38,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.45,
                    low=100.2,
                    open=100.38,
                    close=100.28,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 15),
                ),
                spread=0.01,
                deposit=1000,
            ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=100.35,
                low=100.09,
                open=100.28,
                close=100.11,
                volume=1006,
                close_time=datetime(2025, 1, 1, 0, 20),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "expectations": [],
        "expected_states": [
            "not_ready",
            "orders_uptrend",
            "on_market_uptrend",
        ],
        "expected_cooldown_counter": 0,
        "expected_history": [
            Candle(high=100.7, low=100.5, open=100.58, close=100.68, volume=1003),
                Candle(
                    high=100.75,
                    low=100.5,
                    open=100.68,
                    close=100.58,
                    volume=1002,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                Candle(
                    high=100.65,
                    low=100.4,
                    open=100.58,
                    close=100.48,
                    volume=1003,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                Candle(
                    high=100.55,
                    low=100.3,
                    open=100.48,
                    close=100.38,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                Candle(
                    high=100.45,
                    low=100.2,
                    open=100.38,
                    close=100.28,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 15),
                ),
                Candle(
                    high=100.35,
                    low=100.09,
                    open=100.28,
                    close=100.11,
                    volume=1006,
                    close_time=datetime(2025, 1, 1, 0, 20),
                ),
        ],
        "expected_order": Order(
            action=CandleAction.BUY,
            entry=100.26,
            sl=99.98,
            tp=100.81,
            volume=16.39,
        ),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.HOLD,
        "expected_desicion_order": Order(),
        "expected_desicion_report": Report(),
    },
    {
        "name": "14. Not_ready -> orders_uptrend -> idle. Reversal candle",
        "initial_trade_units": [
            Trade_unit(
                candle=Candle(
                    high=100.6, low=100.5, open=100.55, close=100.58, volume=1002
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.7, low=100.5, open=100.58, close=100.68, volume=1003
                ),
                spread=0.01,
                deposit=1001,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.75,
                    low=100.5,
                    open=100.68,
                    close=100.58,
                    volume=1002,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.65,
                    low=100.4,
                    open=100.58,
                    close=100.48,
                    volume=1003,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.55,
                    low=100.3,
                    open=100.48,
                    close=100.38,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.45,
                    low=100.2,
                    open=100.38,
                    close=100.28,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 15),
                ),
                spread=0.01,
                deposit=1000,
            ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=100.4,
                low=100.21,
                open=100.28,
                close=100.35,
                volume=1006,
                close_time=datetime(2025, 1, 1, 0, 20),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "expectations": [],
        "expected_states": [
            "not_ready",
            "orders_uptrend",
            "on_market_uptrend",
        ],
        "expected_cooldown_counter": 0,
        "expected_history": [
                Candle(high=100.7, low=100.5, open=100.58, close=100.68, volume=1003),
                Candle(
                    high=100.75,
                    low=100.5,
                    open=100.68,
                    close=100.58,
                    volume=1002,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                Candle(
                    high=100.65,
                    low=100.4,
                    open=100.58,
                    close=100.48,
                    volume=1003,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                Candle(
                    high=100.55,
                    low=100.3,
                    open=100.48,
                    close=100.38,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                Candle(
                    high=100.45,
                    low=100.2,
                    open=100.38,
                    close=100.28,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 15),
                ),
                Candle(
                    high=100.4,
                    low=100.21,
                    open=100.28,
                    close=100.35,
                    volume=1006,
                    close_time=datetime(2025, 1, 1, 0, 20),
                ),],
        "expected_order": Order(
            action=CandleAction.BUY,
            entry=100.26,
            sl=99.98,
            tp=100.81,
            volume=16.39,
        ),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.HOLD,
        "expected_desicion_order": Order(),
        "expected_desicion_report": Report(),
    },
    {
        "name": "15. Not_ready -> orders_uptrend -> on_market_uptrend. Candle continues uptrend. SL is not triggered",
        "initial_trade_units": [
            Trade_unit(
                candle=Candle(
                    high=100.6, low=100.5, open=100.55, close=100.58, volume=1002
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.7, low=100.5, open=100.58, close=100.68, volume=1003
                ),
                spread=0.01,
                deposit=1001,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.75,
                    low=100.5,
                    open=100.68,
                    close=100.58,
                    volume=1002,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.65,
                    low=100.4,
                    open=100.58,
                    close=100.48,
                    volume=1003,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.55,
                    low=100.3,
                    open=100.48,
                    close=100.38,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.45,
                    low=100.2,
                    open=100.38,
                    close=100.28,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 15),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.35,
                    low=100.19,
                    open=100.28,
                    close=100.21,
                    volume=1006,
                    close_time=datetime(2025, 1, 1, 0, 20),
                ),
                spread=0.01,
                deposit=1000,
            ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=100.35,
                low=100.25,
                open=100.21,
                close=100.31,
                volume=1006,
                close_time=datetime(2025, 1, 1, 0, 25),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "expectations": [],
        "expected_states": [
            "not_ready",
            "orders_uptrend",
            "on_market_uptrend",
        ],
        "expected_cooldown_counter": 0,
        "expected_history": [
            Candle(
                    high=100.7, low=100.5, open=100.58, close=100.68, volume=1003
                ),
            Candle(
                    high=100.75,
                    low=100.5,
                    open=100.68,
                    close=100.58,
                    volume=1002,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
            Candle(
                    high=100.65,
                    low=100.4,
                    open=100.58,
                    close=100.48,
                    volume=1003,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
            Candle(
                    high=100.55,
                    low=100.3,
                    open=100.48,
                    close=100.38,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
            Candle(
                    high=100.45,
                    low=100.2,
                    open=100.38,
                    close=100.28,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 15),
                ),
            Candle(
                    high=100.35,
                    low=100.19,
                    open=100.28,
                    close=100.21,
                    volume=1006,
                    close_time=datetime(2025, 1, 1, 0, 20),
                ),
            Candle(
                high=100.35,
                low=100.25,
                open=100.21,
                close=100.31,
                volume=1006,
                close_time=datetime(2025, 1, 1, 0, 25),
            ),
        ],
        "expected_order": Order(
            action=CandleAction.BUY,
            entry=100.26,
            sl=99.98,
            tp=100.81,
            volume=16.39,
        ),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.HOLD,
        "expected_desicion_order": Order(),
        "expected_desicion_report": Report(),
    },
    {
        "name": "16. Not_ready -> orders_uptrend -> on_market_uptrend > cooldown. SL is triggered",
        "initial_trade_units": [
            Trade_unit(
                candle=Candle(
                    high=100.6, low=100.5, open=100.55, close=100.58, volume=1002
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.7, low=100.5, open=100.58, close=100.68, volume=1003
                ),
                spread=0.01,
                deposit=1001,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.75,
                    low=100.5,
                    open=100.68,
                    close=100.58,
                    volume=1002,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.65,
                    low=100.4,
                    open=100.58,
                    close=100.48,
                    volume=1003,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.55,
                    low=100.3,
                    open=100.48,
                    close=100.38,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.45,
                    low=100.2,
                    open=100.38,
                    close=100.28,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 15),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.35,
                    low=100.19,
                    open=100.28,
                    close=100.21,
                    volume=1006,
                    close_time=datetime(2025, 1, 1, 0, 20),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.35,
                    low=100.25,
                    open=100.21,
                    close=100.31,
                    volume=1006,
                    close_time=datetime(2025, 1, 1, 0, 25),
                ),
                spread=0.01,
                deposit=1000,
            ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=100.35,
                low=100.09,
                open=100.31,
                close=100.32,
                volume=1006,
                close_time=datetime(2025, 1, 1, 0, 30),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "expectations": [],
        "expected_states": [
            "not_ready",
            "orders_uptrend",
            "on_market_uptrend",
        ],
        "expected_cooldown_counter": 0,
        "expected_history": [
            Candle(
                    high=100.7, low=100.5, open=100.58, close=100.68, volume=1003
                ),
            Candle(
                    high=100.75,
                    low=100.5,
                    open=100.68,
                    close=100.58,
                    volume=1002,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
            Candle(
                    high=100.65,
                    low=100.4,
                    open=100.58,
                    close=100.48,
                    volume=1003,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
            Candle(
                    high=100.55,
                    low=100.3,
                    open=100.48,
                    close=100.38,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
            Candle(
                    high=100.45,
                    low=100.2,
                    open=100.38,
                    close=100.28,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 15),
                ),
            Candle(
                    high=100.35,
                    low=100.19,
                    open=100.28,
                    close=100.21,
                    volume=1006,
                    close_time=datetime(2025, 1, 1, 0, 20),
                ),
            Candle(
                high=100.35,
                low=100.25,
                open=100.21,
                close=100.31,
                volume=1006,
                close_time=datetime(2025, 1, 1, 0, 25),
            ),
            Candle(
                high=100.35,
                low=100.09,
                open=100.31,
                close=100.32,
                volume=1006,
                close_time=datetime(2025, 1, 1, 0, 30),
            ),
        ],
        "expected_order": Order(
            action=CandleAction.BUY,
            entry=100.26,
            sl=99.98,
            tp=100.81,
            volume=16.39,
        ),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.HOLD,
        "expected_desicion_order": Order(),
        "expected_desicion_report": Report(),
    },
    {
        "name": "17. Not_ready -> orders_uptrend -> on_market_uptrend > cooldown. TP is triggered",
        "initial_trade_units": [
            Trade_unit(
                candle=Candle(
                    high=100.6, low=100.5, open=100.55, close=100.58, volume=1002
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.7, low=100.5, open=100.58, close=100.68, volume=1003
                ),
                spread=0.01,
                deposit=1001,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.75,
                    low=100.5,
                    open=100.68,
                    close=100.58,
                    volume=1002,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.65,
                    low=100.4,
                    open=100.58,
                    close=100.48,
                    volume=1003,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.55,
                    low=100.3,
                    open=100.48,
                    close=100.38,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.45,
                    low=100.2,
                    open=100.38,
                    close=100.28,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 15),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.35,
                    low=100.19,
                    open=100.28,
                    close=100.21,
                    volume=1006,
                    close_time=datetime(2025, 1, 1, 0, 20),
                ),
                spread=0.01,
                deposit=1000,
            ),
            Trade_unit(
                candle=Candle(
                    high=100.35,
                    low=100.25,
                    open=100.21,
                    close=100.31,
                    volume=1006,
                    close_time=datetime(2025, 1, 1, 0, 25),
                ),
                spread=0.01,
                deposit=1000,
            ),
        ],
        "trade_unit": Trade_unit(
            candle=Candle(
                high=100.45,
                low=100.25,
                open=100.31,
                close=100.37,
                volume=1006,
                close_time=datetime(2025, 1, 1, 0, 30),
            ),
            spread=0.01,
            deposit=1000,
        ),
        "min_price_delta": 0.01,
        "background": Background.FLAT_REV,
        "power": Power.WEAK,
        "expectations": [],
        "expected_states": [
            "not_ready",
            "orders_uptrend",
            "on_market_uptrend",
        ],
        "expected_cooldown_counter": 0,
        "expected_history": [
            Candle(
                    high=100.7, low=100.5, open=100.58, close=100.68, volume=1003
                ),
            Candle(
                    high=100.75,
                    low=100.5,
                    open=100.68,
                    close=100.58,
                    volume=1002,
                    close_time=datetime(2025, 1, 1, 0, 0),
                ),
            Candle(
                    high=100.65,
                    low=100.4,
                    open=100.58,
                    close=100.48,
                    volume=1003,
                    close_time=datetime(2025, 1, 1, 0, 5),
                ),
            Candle(
                    high=100.55,
                    low=100.3,
                    open=100.48,
                    close=100.38,
                    volume=1004,
                    close_time=datetime(2025, 1, 1, 0, 10),
                ),
            Candle(
                    high=100.45,
                    low=100.2,
                    open=100.38,
                    close=100.28,
                    volume=1005,
                    close_time=datetime(2025, 1, 1, 0, 15),
                ),
            Candle(
                    high=100.35,
                    low=100.19,
                    open=100.28,
                    close=100.21,
                    volume=1006,
                    close_time=datetime(2025, 1, 1, 0, 20),
                ),
            Candle(
                high=100.35,
                low=100.25,
                open=100.21,
                close=100.31,
                volume=1006,
                close_time=datetime(2025, 1, 1, 0, 25),
            ),
            Candle(
                high=100.45,
                low=100.25,
                open=100.31,
                close=100.37,
                volume=1006,
                close_time=datetime(2025, 1, 1, 0, 30),
            ),
        ],
        "expected_order": Order(
            action=CandleAction.BUY,
            entry=100.26,
            sl=99.98,
            tp=100.81,
            volume=16.39,
        ),
        "expected_deposit": 1000,
        "expected_desicion_action": MarketAction.HOLD,
        "expected_desicion_order": Order(),
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
            trade_engine_flat.parameters_store.order_reset()

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
        trade_engine_flat.parameters_store.order_reset()

    add(states, cast(str,trade_engine_flat.current_state_value))

    # Assertions

    assert states == case["expected_states"]

    assert (
        trade_engine_flat.counter_operator.cooldown_counter()
        == case["expected_cooldown_counter"]
    )

    assert trade_engine_flat.history_operator.get() == case["expected_history"]

    assert (
        trade_engine_flat.parameters_store.order().action == case["expected_order"].action
    )

    assert round(trade_engine_flat.parameters_store.order().entry, 2) == round(
        case["expected_order"].entry, 2
    )
    assert round(trade_engine_flat.parameters_store.order().sl, 2) == round(
        case["expected_order"].sl, 2
    )
    assert round(trade_engine_flat.parameters_store.order().tp, 2) == round(
        case["expected_order"].tp, 2
    )
    assert round(trade_engine_flat.parameters_store.order().volume, 2) == round(
        case["expected_order"].volume, 2
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
    assert output.report.order.action == case["expected_desicion_report"].order.action
    assert round(output.report.order.entry, 2) == round(
        case["expected_desicion_report"].order.entry, 2
    )
    assert round(output.report.order.sl, 2) == round(
        case["expected_desicion_report"].order.sl, 2
    )
    assert round(output.report.order.tp, 2) == round(
        case["expected_desicion_report"].order.tp, 2
    )
    assert round(output.report.order.volume, 2) == round(
        case["expected_desicion_report"].order.volume, 2
    )
    assert output.report.reason == case["expected_desicion_report"].reason


def add(states: List[str], state: str) -> None:
    if len(states) == 0 or (len(states) > 0 and states[-1] != state):
        states.append(state)
        #
        #
