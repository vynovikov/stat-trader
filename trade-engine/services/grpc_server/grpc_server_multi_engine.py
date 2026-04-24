import os
import sys

# Получаем путь к текущему скрипту
current_dir = os.path.dirname(os.path.abspath(__file__))

# Поднимаемся на два уровня выше, чтобы попасть в корневой каталог проекта (ml-agent)
# Путь может быть другим, в зависимости от того, где находится config.py
project_root = os.path.abspath(os.path.join(current_dir, "../.."))

# Добавляем корневой каталог в sys.path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import logging
import grpc

from concurrent import futures
from typing import List, cast
from logging import LoggerAdapter
from grpc_reflection.v1alpha import reflection
from datetime import timedelta
from prometheus_client import Gauge, Info, start_http_server
from domain.types.power import Power

from config.config import Config
from domain.models.trade_unit import Trade_unit
from domain.types.background import Background
from domain.types.candle import Candle
from domain.types.candle_action import CandleAction
from domain.types.market_action import MarketAction
from pb import vector_trader_pb2 as pb2
from pb import vector_trader_pb2_grpc as pb2_grpc
from services.bookkeeper.leveraged_bookkeeper import LeveragedBookkeeper
from services.counter_operator.counter_operator import CounterOperatorImpl
from services.parameters_store.parameters_store import ParametersStoreImpl
from services.history_operator.history_operator import HistoryOperatorImpl
from services.report_operator.report_operator import ReportOperatorImpl
from services.log_operator.log_operator import LogOperatorImpl
from services.repository.mock_repository import MockRepository
from services.strategy_operator.strategy_operator_reversal_v5_trend import (
    StrategyOperatorReversalV5,
)
from services.strategy_operator.strategy_operator_continual_v6_trend import (
    StrategyOperatorContinualV6,
)
from services.trade_engine.interface import TradeEngine
from services.trade_engine.trade_engine_reversal_v5 import TradeEngineReversalV5
from services.trade_engine.trade_engine_continual_v6 import TradeEngineContinualV6
from services.trade_engine.trade_engine_adapter import (
    TradeEngineAdapter,
)
from services.window_operator.window_operator import WindowOperatorImpl
from services.metric_repository.clickhouse_metric_repository import (
    ClickhouseMetricRepository,
)
from services.metric_repository.async_metric_repository import AsyncMetricRepository
from services.usecases.interface import Usecases
from services.metric_repository.interface import MetricRepository
from services.trade_engine.trade_engine_adapter import (
    TradeEngineAdapter,
)
from services.usecases.usecases_multi_engine import UsecasesMultiEngine

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


def trade_engine_rev_v5(
    cfg: Config,
    metric_repository: MetricRepository,
) -> TradeEngine:
    engine_logger = get_logger(str({cfg.ENGINE_LABEL_REV}))
    strategy_logger = get_logger(str({cfg.STRATEGY_OPERATOR_LABEL_REV}))

    repository = MockRepository()
    strategy_operator = StrategyOperatorReversalV5(
        bookkeeper=LeveragedBookkeeper(leverage=10),
        metric_repository=metric_repository,
        logger=strategy_logger,
    )
    history_operator = HistoryOperatorImpl()
    window_operator = WindowOperatorImpl(maxlen_window=6)
    counter_operator = CounterOperatorImpl(cooldown_counter_max=4)
    report_operator = ReportOperatorImpl()
    log_operator = LogOperatorImpl()
    parameters_store = ParametersStoreImpl(
        prelude_len=3,
        window_len=6,
        risk_per_trade=cfg.RISK_PER_TRADE,
        min_volume=0.02,
        engine_service_name=cfg.ENGINE_LABEL_REV,
        strategy_operator_service_name=cfg.STRATEGY_OPERATOR_LABEL_REV,
        background=Background(cfg.BACKGROUND),
        power=Power(cfg.POWER),
        body_ratio=cfg.BODY_RATIO,
        shadow_ratio=cfg.SHADOW_RATIO,
    )

    trade_engine_rev_v5 = TradeEngineReversalV5(
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

    return TradeEngineAdapter(trade_engine_rev_v5)

def trade_engine_con_v6(
    cfg: Config,
    metric_repository: MetricRepository,
) -> TradeEngine:
    engine_logger = get_logger(str({cfg.ENGINE_LABEL_CON}))
    strategy_logger = get_logger(str({cfg.STRATEGY_OPERATOR_LABEL_CON}))

    repository = MockRepository()
    strategy_operator = StrategyOperatorContinualV6(
        bookkeeper=LeveragedBookkeeper(leverage=10),
        metric_repository=metric_repository,
        logger=strategy_logger,
    )
    history_operator = HistoryOperatorImpl()
    window_operator = WindowOperatorImpl(maxlen_window=6)
    counter_operator = CounterOperatorImpl(cooldown_counter_max=4)
    report_operator = ReportOperatorImpl()
    log_operator = LogOperatorImpl()
    parameters_store = ParametersStoreImpl(
        prelude_len=3,
        window_len=6,
        risk_per_trade=cfg.RISK_PER_TRADE*2,
        min_volume=0.02,
        engine_service_name=cfg.ENGINE_LABEL_CON,
        strategy_operator_service_name=cfg.STRATEGY_OPERATOR_LABEL_CON,
        background=Background(cfg.BACKGROUND),
        power=Power(cfg.POWER),
        body_ratio=cfg.BODY_RATIO,
        shadow_ratio=cfg.SHADOW_RATIO,
    )

    trade_engine_con_v6 = TradeEngineContinualV6(
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

    return TradeEngineAdapter(trade_engine_con_v6)


def get_warmup_candles(
    backend_address: str, symbol: str, timeframe: str, limit: int
) -> List[Candle]:
    channel = grpc.insecure_channel(backend_address)
    candles: List[Candle] = []

    try:
        stub = pb2_grpc.StockStub(channel)

        req = pb2.LastNRequest(
            symbol=symbol,
            interval=timeframe,
            limit=limit,
        )

        resp: pb2.LastNResponse = stub.LastNCandles(req)

        candles_raw = list(resp.candles)
        # На случай, если backend вернёт неотсортированные данные
        candles_raw.sort(key=lambda c: c.close_time.ToDatetime())
        candles_raw = candles_raw[-limit:]

        for c in candles_raw:
            candles.append(
                Candle(
                    open=c.open,
                    high=c.high,
                    low=c.low,
                    close=c.close,
                    volume=c.volume,
                    close_time=c.close_time.ToDatetime(),
                )
            )

    finally:
        channel.close()

    return candles


def to_pb_candle_action(action: CandleAction) -> pb2.CandleAction:
    return cast(
        pb2.CandleAction,
        pb2.CandleAction.Value(action.name),
    )


def to_pb_market_action(action: MarketAction) -> pb2.MarketAction:
    return cast(
        pb2.MarketAction,
        pb2.MarketAction.Value(action.name),
    )


class DecideService(pb2_grpc.EngineServicer):
    def __init__(
        self,
        usecases: Usecases,
    ):
        self.usecases = usecases

    def Decide(self, request, context):
        balance = request.balance

        trade_unit = Trade_unit(
            candle=Candle(
                open=request.candle.open,
                high=request.candle.high,
                low=request.candle.low,
                close=request.candle.close,
                volume=request.candle.volume,
                open_time=(request.candle.open_time.ToDatetime()+
                           timedelta(
                               seconds=1,
                               )).replace(
                                    second=0,
                                    microsecond=0,
                                ),
                close_time=(request.candle.close_time.ToDatetime()+
                            timedelta(
                                seconds=1,
                                )).replace(
                                    second=0,
                                    microsecond=0,
                                ),
            ),
            spread=request.spread,
            deposit=balance,
        )

        decision = self.usecases.decide(trade_unit)

        return pb2.DecideResponse(
            market_action=to_pb_market_action(decision.action),
            order=pb2.Order(
                entry=decision.order.entry,
                sl=decision.order.sl,
                tp=decision.order.tp,
                volume=decision.order.volume,
                candle_action=to_pb_candle_action(decision.order.action),
            ),
            profit=0,
        )


def serve(cfg: Config) -> None:
    symbol = cfg.SYMBOL
    timeframe = cfg.TIMEFRAME
    backend_address = cfg.BACKEND_ADDR

    metric_repository = ClickhouseMetricRepository(
        host=cfg.CLICKHOUSE_HOST,
        port=cfg.CLICKHOUSE_PORT,
        username=cfg.CLICKHOUSE_USER,
        password=cfg.CLICKHOUSE_PASS,
        database=cfg.CLICKHOUSE_DB,
    )

    async_metric_repository = AsyncMetricRepository(metric_repository)

    trade_engine_power = Gauge(
        "trade_engine_power",
        "Power (2=WEAK, 3=STRONG)",
    )
    trade_engine_power.set(Power(cfg.POWER).value)

    trade_engine_background = Gauge(
        "trade_engine_background",
        "Trade engine background",
    )
    trade_engine_background.set(Background(cfg.BACKGROUND).value)

    print(f"Starting metrics server on :5500")
    start_http_server(5500)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))

    warmup_candles = get_warmup_candles(
        backend_address=backend_address,
        symbol=symbol,
        timeframe=timeframe,
        limit=5,
    )

    print(f"background {Background(cfg.BACKGROUND).name}")

    engine_rev_v5 = trade_engine_rev_v5(cfg,async_metric_repository)
    engine_con_v6 = trade_engine_con_v6(cfg,async_metric_repository)

    engines=[engine_rev_v5,engine_con_v6]

    usecases=UsecasesMultiEngine(
        trade_engines=engines,
        metric_repository=async_metric_repository,

    )

    for candle in warmup_candles:
        trade_unit = Trade_unit(
            candle=candle,
            spread=0.01,
            deposit=1000.0,
        )
        for engine in engines:
            engine.handle_first(trade_unit)

    service = DecideService(
        usecases=usecases,
    )

    pb2_grpc.add_EngineServicer_to_server(service, server)

    SERVICE_NAMES = (
        pb2.DESCRIPTOR.services_by_name["Engine"].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)

    port = server.add_insecure_port(f"[::]{cfg.LOCAL_ADDR}")
    if port == 0:
        raise RuntimeError(f"Failed to bind to port {cfg.LOCAL_ADDR}")
    server.start()

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\nShutting down gRPC server...")
        server.stop(grace=0)


if __name__ == "__main__":
    cfg = Config.from_env()
    print(f"Starting [{cfg.ENGINE_LABEL_REV} + {cfg.ENGINE_LABEL_CON}] on port {cfg.LOCAL_ADDR}...")
    serve(cfg)
