import os
import sys

# Получаем путь к текущему скрипту
current_dir = os.path.dirname(os.path.abspath(__file__))

# Поднимаемся на два уровня выше, чтобы попасть в корневой каталог проекта (ml-agent)
# Путь может быть другим, в зависимости от того, где находится config.py
project_root = os.path.abspath(os.path.join(current_dir, ".."))

# Добавляем корневой каталог в sys.path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from domain.models.trade_unit import Trade_unit
from domain.types.market_action import MarketAction
from services.bookkeeper.leveraged_bookkeeper import LeveragedBookkeeper
from services.counter_operator.counter_operator import CounterOperatorImpl
from services.parameters_store.parameters_store import ParametersStoreImpl
from services.plotter.plotter import Plotter
from services.history_operator.history_operator import HistoryOperatorImpl
from services.report_operator.report_operator import ReportOperatorImpl
from services.repository import QdrantRepository
from services.strategy_operator.reversal_strategy_operator_v3 import (
    ReversalStrategyOperatorV3,
)
from services.trade_engine.trade_engine_reversal_v3 import TradeEngineReversalV3
from services.window_operator.window_operator import WindowOperatorImpl
from utils.candle_utils import get_candles
from utils.read_data import read_data


if __name__ == "__main__":
    plotter = Plotter("data/candles/BTCUSDT/output")

    repository = QdrantRepository("BTCUSDT")
    leveraged_bookkeeper = LeveragedBookkeeper(leverage=2)
    reversal_strategy_operator = ReversalStrategyOperatorV3(leveraged_bookkeeper)
    history_operator = HistoryOperatorImpl()
    window_operator = WindowOperatorImpl()
    counter_operator = CounterOperatorImpl()
    report_operator = ReportOperatorImpl()
    parameters_store = ParametersStoreImpl(
        deposit=1000,
        prelude_len=4,
        window_len=6,
        risk_per_trade=0.01,
        min_volume=0.02,
    )

    trade_engine_v3 = TradeEngineReversalV3(
        repository=repository,
        strategy_operator=reversal_strategy_operator,
        history_operator=history_operator,
        window_operator=window_operator,
        counter_operator=counter_operator,
        report_operator=report_operator,
        parameters_store=parameters_store,
    )

    candles_df = read_data(
        input_file="data/candles/BTCUSDT/full/btcusdt_5m_2025-10_11.csv",
        offset_hours=24 * 7 * 0,
        limit_hours=24 * 7 * 8,
    )
    candles = get_candles(candles_df)
    deal_number = 0

    for candle in candles:
        trade_unit = Trade_unit(
            candle=candle,
            spread=0.01,
            deposit=trade_engine_v3.parameters_store.deposit(),
        )
        decision = trade_engine_v3.handle_first(
            trade_unit=trade_unit,
        )
        if decision.action == MarketAction.CLOSE:
            print(
                f"{deal_number}. {decision.report.reason}. Deposit: {round(trade_engine_v3.parameters_store.deposit(),0)}"
            )

            deal_number += 1

            # plotter.plot_full(
            #    candles=decision.report.candles,
            #    spread=trade_unit.spread,
            #    order=decision.report.order,
            #    folder_name="",
            #    file_name=str(deal_number),
            #    reason=decision.report.reason,
            # )
            trade_engine_v3.parameters_store.order_reset()
            trade_engine_v3.parameters_store.clear_report()
