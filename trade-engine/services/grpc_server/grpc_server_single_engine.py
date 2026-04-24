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
from concurrent import futures
from typing import List, cast

import grpc
from grpc_reflection.v1alpha import reflection

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
from services.repository.mock_repository import MockRepository
from services.strategy_operator.strategy_operator_reversal_v5_trend import (
    StrategyOperatorReversalV5,
)
from services.priority_operator.priority_operator import PriorityOperator
from services.trade_engine.trade_engine_reversal_v5 import TradeEngineReversalV5
from services.window_operator.window_operator import WindowOperatorImpl
from services.metric_repository.interface import MetricRepository
from services.metric_repository.clickhouse_metric_repository import (
    ClickhouseMetricRepository,
)
from services.usecases.interface import Usecases
from services.usecases.single_engine_usecases import SingleEngineUsecases
from services.trade_engine.trade_engine_adapter import (
    TradeEngineAdapter,
)


def trade_engine(
    cfg: Config,
    stream_handler: logging.StreamHandler,
) -> TradeEngineReversalV5:
    base_logger = logging.getLogger(cfg.VERSION)
    base_logger.setLevel(logging.INFO)
    base_logger.addHandler(stream_handler)

    logger = logging.LoggerAdapter(base_logger, {"engine_id": cfg.VERSION})

    repository = MockRepository()
    strategy_operator = StrategyOperatorReversalV5(LeveragedBookkeeper(leverage=10))
    history_operator = HistoryOperatorImpl()
    window_operator = WindowOperatorImpl(maxlen_window=6)
    counter_operator = CounterOperatorImpl(cooldown_counter_max=4)
    report_operator = ReportOperatorImpl()
    parameters_store = ParametersStoreImpl(
        prelude_len=3,
        window_len=6,
        risk_per_trade=0.005,
        min_volume=0.02,
        engine_id=cfg.VERSION,
        background=Background(cfg.BACKGROUND),
        body_ratio=cfg.BODY_RATIO,
        shadow_ratio=cfg.SHADOW_RATIO,
    )

    engine = TradeEngineReversalV5(
        repository=repository,
        strategy_operator=strategy_operator,
        history_operator=history_operator,
        window_operator=window_operator,
        counter_operator=counter_operator,
        report_operator=report_operator,
        parameters_store=parameters_store,
        logger=logger,
    )

    return engine


def get_warmup_candles(
    backend_address: str, symbol: str, timeframe: str, limit: int
) -> List[Candle]:
    """
    Берём последние N свечей через новую ручку LastNCandles.

    Важно:
    - LastNCandles возвращает не поток, а единичный ответ LastNResponse.
    - На всякий случай сортируем по close_time и берём последние limit штук.
    """
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

        self.trade_id: int = 0

    def Decide(self, request, context):
        balance = request.balance

        trade_unit = Trade_unit(
            candle=Candle(
                open=request.candle.open,
                high=request.candle.high,
                low=request.candle.low,
                close=request.candle.close,
                volume=request.candle.volume,
                close_time=request.candle.close_time.ToDatetime(),
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

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))

    warmup_candles = get_warmup_candles(
        backend_address=backend_address,
        symbol=symbol,
        timeframe=timeframe,
        limit=5,
    )

    print(f"background {Background(cfg.BACKGROUND).name}")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("    - %(levelname)s: [%(engine_id)s] %(message)s")
    console_handler.setFormatter(formatter)

    engine = trade_engine(cfg, console_handler)

    for candle in warmup_candles:
        trade_unit = Trade_unit(
            candle=candle,
            spread=0.01,
            deposit=1000.0,
        )
        engine.handle_first(trade_unit)

    trade_engine_adapter = TradeEngineAdapter(engine)

    usecases = SingleEngineUsecases(
        trade_engine=trade_engine_adapter, metric_repository=metric_repository
    )

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
        # сюда прилетает Ctrl+C, стек уже не печатается
        print("\nShutting down gRPC server...")
        # graceful shutdown; можно поставить секунду, если хочешь дождаться RPC
        server.stop(grace=0)


if __name__ == "__main__":
    cfg = Config.from_env()
    print(f"Starting [{cfg.VERSION}] on port {cfg.LOCAL_ADDR}...")
    serve(cfg)
