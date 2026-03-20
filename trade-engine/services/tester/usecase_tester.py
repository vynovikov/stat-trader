import logging
import os
import sys

import grpc

# Получаем путь к текущему скрипту
current_dir = os.path.dirname(os.path.abspath(__file__))

# Поднимаемся на два уровня выше, чтобы попасть в корневой каталог проекта (ml-agent)
# Путь может быть другим, в зависимости от того, где находится config.py
project_root = os.path.abspath(os.path.join(current_dir, "../.."))

# Добавляем корневой каталог в sys.path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from datetime import datetime, timedelta
from logging import LoggerAdapter
from typing import List

from config.config import Config
from domain.constants.constants import Constants
from domain.models.trade_unit import Trade_unit
from domain.types.background import Background
from domain.types.candle import Candle
from domain.types.market_action import MarketAction
from domain.types.power import Power
from pb import vector_trader_pb2 as pb2
from pb import vector_trader_pb2_grpc as pb2_grpc
from services.bookkeeper.leveraged_bookkeeper import LeveragedBookkeeper
from services.counter_operator.counter_operator import CounterOperatorImpl
from services.history_operator.history_operator import HistoryOperatorImpl
from services.metric_repository.interface import MetricRepository
from services.metric_repository.clickhouse_metric_repository import (
    ClickhouseMetricRepository,
)
from services.parameters_store.parameters_store import ParametersStoreImpl
from services.report_operator.report_operator import ReportOperatorImpl
from services.repository.mock_repository import MockRepository
from services.strategy_operator.strategy_operator_continual_v6 import (
    StrategyOperatorContinualV6,
)
from services.strategy_operator.strategy_operator_reversal_v5 import (
    StrategyOperatorReversalV5,
)
from services.trade_engine.interface import TradeEngine
from services.trade_engine.trade_engine_adapter import TradeEngineAdapter
from services.trade_engine.trade_engine_continual_v6 import TradeEngineContinualV6
from services.trade_engine.trade_engine_reversal_v5 import TradeEngineReversalV5
from services.usecases.usecases_multi_engine import UsecasesMultiEngine
from services.window_operator.window_operator import WindowOperatorImpl
from services.log_operator.log_operator import LogOperatorImpl


def get_logger(label: str) -> LoggerAdapter:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)

    formatter = logging.Formatter("    - %(levelname)s: [%(engine_id)s] %(message)s")
    stream_handler.setFormatter(formatter)

    base_logger = logging.getLogger(label)
    base_logger.setLevel(logging.INFO)
    base_logger.addHandler(stream_handler)

    logger = logging.LoggerAdapter(base_logger, {"engine_id": label})

    return logger


def get_reversal_v5(
    initial_deposit: float,
    metric_repository: MetricRepository,
    cfg: Config,
) -> TradeEngine:
    engine_logger = get_logger(str({cfg.ENGINE_LABEL_REV}))
    strategy_logger = get_logger(str({cfg.STRATEGY_OPERATOR_LABEL_REV}))

    repository = MockRepository()
    leveraged_bookkeeper = LeveragedBookkeeper(leverage=10)
    strategy_operator = StrategyOperatorReversalV5(
        bookkeeper=leveraged_bookkeeper,
        metric_repository=metric_repository,
        logger=strategy_logger,
    )
    history_operator = HistoryOperatorImpl()

    window_operator = WindowOperatorImpl(maxlen_window=6)

    counter_operator = CounterOperatorImpl(cooldown_counter_max=4)
    report_operator = ReportOperatorImpl()
    log_operator = LogOperatorImpl()
    parameters_store = ParametersStoreImpl(
        prelude_len=4,
        window_len=6,
        risk_per_trade=cfg.RISK_PER_TRADE,
        deposit=initial_deposit,
        engine_service_name=cfg.ENGINE_LABEL_REV,
        strategy_operator_service_name=cfg.STRATEGY_OPERATOR_LABEL_REV,
        background=Background(cfg.BACKGROUND),
        power=Power(cfg.POWER),
        min_price_delta=cfg.MIN_PRICE_DELTA,
        body_ratio=cfg.BODY_RATIO,
        shadow_ratio=cfg.SHADOW_RATIO,
    )

    trade_engine_reversal_v5 = TradeEngineReversalV5(
        repository=repository,
        strategy_operator=strategy_operator,
        history_operator=history_operator,
        window_operator=window_operator,
        counter_operator=counter_operator,
        report_operator=report_operator,
        log_operator=log_operator,
        parameters_store=parameters_store,
        metric_repository=metric_repository,
        logger=engine_logger,
    )

    return TradeEngineAdapter(trade_engine_reversal_v5)


def get_continual_v6(
    initial_deposit: float,
    metric_repository: MetricRepository,
    cfg: Config,
) -> TradeEngine:
    engine_logger = get_logger(str({cfg.ENGINE_LABEL_CON}))
    strategy_logger = get_logger(str({cfg.STRATEGY_OPERATOR_LABEL_CON}))

    repository = MockRepository()
    leveraged_bookkeeper = LeveragedBookkeeper(leverage=10)
    strategy_operator = StrategyOperatorContinualV6(
        bookkeeper=leveraged_bookkeeper,
        metric_repository=metric_repository,
        logger=strategy_logger,
    )
    history_operator = HistoryOperatorImpl()

    window_operator = WindowOperatorImpl(maxlen_window=6)

    counter_operator = CounterOperatorImpl(cooldown_counter_max=4)
    report_operator = ReportOperatorImpl()
    log_operator = LogOperatorImpl()
    parameters_store = ParametersStoreImpl(
        prelude_len=4,
        window_len=6,
        risk_per_trade=cfg.RISK_PER_TRADE*2,
        deposit=initial_deposit,
        engine_service_name=cfg.ENGINE_LABEL_CON,
        strategy_operator_service_name=cfg.STRATEGY_OPERATOR_LABEL_CON,
        background=Background(cfg.BACKGROUND),
        power=Power(cfg.POWER),
        min_price_delta=cfg.MIN_PRICE_DELTA,
        body_ratio=cfg.BODY_RATIO,
        shadow_ratio=cfg.SHADOW_RATIO,
    )

    trade_engine_continual_v6 = TradeEngineContinualV6(
        repository=repository,
        strategy_operator=strategy_operator,
        history_operator=history_operator,
        window_operator=window_operator,
        counter_operator=counter_operator,
        report_operator=report_operator,
        log_operator=log_operator,
        parameters_store=parameters_store,
        metric_repository=metric_repository,
        logger=engine_logger,
    )
    return TradeEngineAdapter(trade_engine_continual_v6)


def get_candles(
    symbol: str, timeframe: str, from_time: datetime, to_time: datetime
) -> List[Candle]:
    channel = grpc.insecure_channel("localhost:5000")
    candles: List[Candle] = []

    try:
        stub = pb2_grpc.StockStub(channel)

        req = pb2.IntervalCandlesRequest(
            symbol=symbol,
            interval=timeframe,
            from_timestamp=int(from_time.timestamp()),
            to_timestamp=int(to_time.timestamp()),
        )

        resp: pb2.IntervalCandlesResponse = stub.IntervalCandles(req)

        candles_raw = list(resp.candles)
        candles_raw.sort(key=lambda c: c.close_time.ToDatetime())

        for c in candles_raw:
            open_time_dt = (
                c.open_time.ToDatetime()
                + timedelta(
                    seconds=1,
                )
            ).replace(
                second=0,
                microsecond=0,
            )
            close_time_dt = (
                c.close_time.ToDatetime()
                + timedelta(
                    seconds=1,
                )
            ).replace(
                second=0,
                microsecond=0,
            )

            if open_time_dt.tzinfo is None:
                if close_time_dt.tzinfo is not None:
                    close_time_dt = close_time_dt.replace(tzinfo=None)
            else:
                close_time_dt = close_time_dt.replace(tzinfo=None)
                open_time_dt = open_time_dt.replace(tzinfo=None)

            candles.append(
                Candle(
                    open=c.open,
                    high=c.high,
                    low=c.low,
                    close=c.close,
                    volume=c.volume,
                    open_time=open_time_dt,
                    close_time=close_time_dt,
                )
            )

    finally:
        channel.close()

    return candles


if __name__ == "__main__":
    cfg = Config.from_env()

    print(f"Background: {Background(cfg.BACKGROUND).name}")
    print(f"Power: {Power(cfg.POWER).name}\n")

    metric_repository = ClickhouseMetricRepository(
        host="localhost",
        port=8123,
        username="vt_user",
        password="vt_pass",
        database="default",
    )

    metric_repository.truncate_real_tables()
    metric_repository.truncate_logs_tables()

    initial_ballance = 2000
    trade_engine_reversal_v5 = get_reversal_v5(
        initial_deposit=initial_ballance,
        metric_repository=metric_repository,
        cfg=cfg,
    )

    trade_engine_continual_v6 = get_continual_v6(
        initial_deposit=initial_ballance,
        metric_repository=metric_repository,
        cfg=cfg,
    )

    usecases = UsecasesMultiEngine(
        trade_engines=[trade_engine_reversal_v5, trade_engine_continual_v6],
        metric_repository=metric_repository,
    )

    candles = get_candles(
        "BTCUSDT",
        "15m",
        from_time=datetime(2026, 3, 6, 5, 0, 0),
        to_time=datetime(2026, 3, 6, 20, 15, 0),
    )

    profit = 0
    profit_trades = 0
    loss_trades = 0
    sl_trades = 0
    total_trades = 0

    for candle in candles:
        print(
            f"----------------------------------------------------------------------------------------"
        )
        trade_unit = Trade_unit(
            candle,
            spread=0.01,
            deposit=initial_ballance,
        )

        decision = usecases.decide(trade_unit)

        match decision.action:
            case MarketAction.CLOSE:
                profit += decision.report.profit
                match True:
                    case _ if (
                        decision.report.reason == Constants.BUY_TP
                        or decision.report.reason == Constants.SELL_TP
                    ):
                        profit_trades += 1
                    case _ if (
                        decision.report.reason == Constants.BUY_LOSS
                        or decision.report.reason == Constants.SELL_LOSS
                    ):
                        loss_trades += 1
                    case _ if (
                        decision.report.reason == Constants.BUY_SL
                        or decision.report.reason == Constants.SELL_SL
                    ):
                        sl_trades += 1

                metric_repository.insert_trade_historical(
                    id=total_trades,
                    symbol="BTCUSDT",
                    open_time=decision.report.order.time,
                    engine_id=decision.engine_id,
                    candle_action=decision.report.order.action,
                    reason=decision.report.reason,
                    entry_price=decision.report.order.entry,
                    stop_loss=decision.report.order.sl,
                    take_profit=decision.report.order.tp,
                    volume=decision.report.order.volume,
                    profit=decision.report.profit,
                )

                metric_repository.insert_candles_historical(
                    symbol="BTCUSDT",
                    timeframe="5m",
                    candles=decision.report.candles,
                    engine_id=decision.engine_id,
                    trade_id=total_trades,
                )

                total_trades += 1
                usecases.reports_reset()

    # async_metric_repository.shutdown(timeout=1)
    print(f"\n=== Final Stats ===")

    print(
        f"Total trades: {total_trades}, "
        f"Profit: {profit:.2f} "
        f"[Profit trades: {profit_trades} "
        f"({(profit_trades / total_trades * 100) if total_trades > 0 else 0:.2f}%) | Loss trades {loss_trades} ({(loss_trades / total_trades * 100) if total_trades > 0 else 0:.2f}%) | SL trades: {sl_trades} ({(sl_trades / total_trades * 100) if total_trades > 0 else 0:.2f}%)]"
    )
