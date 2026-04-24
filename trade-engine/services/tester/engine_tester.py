import os
import sys
import logging

# Получаем путь к текущему скрипту
current_dir = os.path.dirname(os.path.abspath(__file__))

# Поднимаемся на два уровня выше, чтобы попасть в корневой каталог проекта (ml-agent)
# Путь может быть другим, в зависимости от того, где находится config.py
project_root = os.path.abspath(os.path.join(current_dir, "../.."))

# Добавляем корневой каталог в sys.path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from datetime import datetime, timedelta
from typing import List

import grpc

from config.config import Config

from domain.models.stat import Stat
from domain.models.trade_unit import Trade_unit

from domain.types.market_action import MarketAction
from domain.types.candle import Candle
from domain.types.background import Background
from domain.types.power import Power

from domain.constants.constants import Constants

from pb import vector_trader_pb2 as pb2
from pb import vector_trader_pb2_grpc as pb2_grpc

from services.bookkeeper.leveraged_bookkeeper import LeveragedBookkeeper
from services.counter_operator.counter_operator import CounterOperatorImpl
from services.parameters_store.parameters_store import ParametersStoreImpl
from services.history_operator.history_operator import HistoryOperatorImpl
from services.report_operator.report_operator import ReportOperatorImpl
from services.repository.mock_repository import MockRepository
from services.strategy_operator.strategy_operator_reversal_v5_trend import (
    StrategyOperatorReversalV5,
)
from services.strategy_operator.strategy_operator_continual_v6_trend import (
    StrategyOperatorContinualV6,
)

from services.trade_engine.trade_engine_adapter import (
    TradeEngineAdapter,
)
from services.trade_engine.trade_engine_reversal_v5 import TradeEngineReversalV5
from services.trade_engine.trade_engine_continual_v6 import TradeEngineContinualV6
from services.window_operator.window_operator import WindowOperatorImpl

from services.metric_repository.clickhouse_metric_repository import (
    ClickhouseMetricRepository,
)
from services.metric_repository.async_metric_repository import (
    AsyncMetricRepository,
)


def get_reversal_v5(
    initial_deposit: float,
    cfg: Config,
    stream_handler: logging.StreamHandler,
) -> TradeEngineAdapter:
    base_logger = logging.getLogger(cfg.VERSION)
    base_logger.setLevel(logging.INFO)
    base_logger.addHandler(stream_handler)

    logger = logging.LoggerAdapter(base_logger, {"engine_id": "rev_v5"})

    repository = MockRepository()
    leveraged_bookkeeper = LeveragedBookkeeper(leverage=10)
    strategy_operator = StrategyOperatorReversalV5(leveraged_bookkeeper)
    history_operator = HistoryOperatorImpl()

    window_operator = WindowOperatorImpl(maxlen_window=6)

    counter_operator = CounterOperatorImpl(cooldown_counter_max=4)
    report_operator = ReportOperatorImpl()
    parameters_store = ParametersStoreImpl(
        prelude_len=4,
        window_len=6,
        risk_per_trade=0.005,
        deposit=initial_deposit,
        engine_id="rev_v5",
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
        parameters_store=parameters_store,
        logger=logger,
    )
    return TradeEngineAdapter(trade_engine_reversal_v5)


def get_continual_v6(
    initial_deposit: float,
    cfg: Config,
    stream_handler: logging.StreamHandler,
) -> TradeEngineAdapter:
    base_logger = logging.getLogger(cfg.VERSION)
    base_logger.setLevel(logging.INFO)
    base_logger.addHandler(stream_handler)

    logger = logging.LoggerAdapter(base_logger, {"engine_id": "con_v6"})

    repository = MockRepository()
    leveraged_bookkeeper = LeveragedBookkeeper(leverage=10)
    strategy_operator = StrategyOperatorContinualV6(leveraged_bookkeeper)
    history_operator = HistoryOperatorImpl()

    window_operator = WindowOperatorImpl(maxlen_window=6)

    counter_operator = CounterOperatorImpl(cooldown_counter_max=4)
    report_operator = ReportOperatorImpl()
    parameters_store = ParametersStoreImpl(
        prelude_len=4,
        window_len=6,
        risk_per_trade=0.005,
        deposit=initial_deposit,
        engine_id="con_v6",
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
        parameters_store=parameters_store,
        logger=logger,
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
            open_time_dt = c.open_time.ToDatetime().replace(second=0, microsecond=0)
            close_time_dt = (c.close_time.ToDatetime() + timedelta(seconds=1)).replace(
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

    stats: List[Stat] = []

    metric_repository = ClickhouseMetricRepository(
        host="localhost",
        port=8123,
        username="vt_user",
        password="vt_pass",
        database="default",
    )

    metric_repository.truncate_historical_tables()

    async_metric_repository = AsyncMetricRepository(metric_repository)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("    - %(levelname)s: [%(engine_id)s] %(message)s")
    console_handler.setFormatter(formatter)

    initial_ballance = 2000
    adapter_reversal_v5 = get_reversal_v5(
        initial_deposit=initial_ballance,
        cfg=cfg,
        stream_handler=console_handler,
    )

    adapter_continual_v6 = get_continual_v6(
       initial_deposit=initial_ballance,
       cfg=cfg,
       stream_handler=console_handler,
    )

    stats.append(Stat(f"[rev_v5]", adapter_reversal_v5))
    stats.append(Stat(f"[con_v6]", adapter_continual_v6))

    candles = get_candles(
        "BTCUSDT",
        "15m",
        from_time=datetime(2026, 2, 24, 15, 30, 0),
        to_time=datetime(2026, 2, 24, 20, 15, 0),
    )

    for candle in candles:
        for stat in stats:
            trade_unit = Trade_unit(
                candle,
                spread=0.01,
                deposit=stat.trade_engine.deposit(),
            )

            decision = stat.trade_engine.handle_first(trade_unit)

            match decision.action:
                case MarketAction.CLOSE:
                    stat.profit += decision.report.profit
                    match True:
                        case _ if (
                            decision.report.reason == Constants.BUY_TP
                            or decision.report.reason == Constants.SELL_TP
                        ):
                            stat.profit_trades += 1
                        case _ if (
                            decision.report.reason == Constants.BUY_LOSS
                            or decision.report.reason == Constants.SELL_LOSS
                        ):
                            stat.loss_trades += 1
                        case _ if (
                            decision.report.reason == Constants.BUY_SL
                            or decision.report.reason == Constants.SELL_SL
                        ):
                            stat.sl_trades += 1

                    async_metric_repository.insert_trade_historical(
                        id=stat.total_trades,
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

                    async_metric_repository.insert_candles_historical(
                        symbol="BTCUSDT",
                        timeframe="5m",
                        candles=decision.report.candles,
                        engine_id=decision.engine_id,
                        trade_id=stat.total_trades,
                    )

                    stat.total_trades += 1
                    stat.trade_engine.report_reset()

    async_metric_repository.shutdown(timeout=1)
    print(f"\n=== Final Stats ===")

    for stat in stats:
        print(
            f"{stat.name} Total trades: {stat.total_trades}, "
            f"Profit: {stat.profit:.2f} "
            f"[Profit trades: {stat.profit_trades} "
            f"({(stat.profit_trades / stat.total_trades * 100) if stat.total_trades > 0 else 0:.2f}%) | Loss trades {stat.loss_trades} ({(stat.loss_trades / stat.total_trades * 100) if stat.total_trades > 0 else 0:.2f}%) | SL trades: {stat.sl_trades} ({(stat.sl_trades / stat.total_trades * 100) if stat.total_trades > 0 else 0:.2f}%)]"
        )
