import traceback
import threading
from queue import Queue, Empty
from typing import List, Optional
from datetime import datetime

from domain.types.candle import Candle
from domain.types.candle_action import CandleAction
from services.metric_repository.interface import MetricRepository


class AsyncMetricRepository(MetricRepository):

    def __init__(
        self,
        repository: MetricRepository,
        max_queue_size: int = 100):

        self.repository = repository
        self.queue = Queue(maxsize=max_queue_size)
        self.running = True

        self.worker = threading.Thread(target=self._worker, daemon=True)
        self.worker.start()

    def _worker(self):

        while self.running:
            try:
                task = self.queue.get(timeout=1)

            except Empty:
                continue

            if task is None:
                break

            try:
                func, args, kwargs = task
                func(*args, **kwargs)

            except Exception as e:
                traceback.print_exc()

            finally:
                self.queue.task_done()

    def insert_candles_all(
        self,
        symbol: str,
        timeframe: str,
        candles: List[Candle],
    ) -> None:
        self.queue.put(
            (
                self.repository.insert_candles_all,
                (
                    symbol,
                    timeframe,
                    candles,
                    ),
                {},
            )
        )

    def insert_candles_traded(
        self,
        symbol: str,
        timeframe: str,
        candles: List[Candle],
        engine_id: str,
        trade_id: Optional[int] = None,
    ) -> None:
        self.queue.put(
            (
                self.repository.insert_candles_traded,
                (
                    symbol,
                    timeframe,
                    candles,
                    engine_id,
                    trade_id,
                    ),
                {},
            )
        )

    def insert_trade_real(
        self,
        id: int,
        symbol: str,
        open_time: datetime,
        engine_id: str,
        candle_action: CandleAction,
        reason: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        volume: float,
        profit: float,
    ) -> None:
        self.queue.put(
            (
                self.repository.insert_trade_real,
                (
                    id,
                    symbol,
                    open_time,
                    engine_id,
                    candle_action,
                    reason,
                    entry_price,
                    stop_loss,
                    take_profit,
                    volume,
                    profit,
                ),
                {},
            )
        )

    def insert_candles_historical(
        self,
        symbol: str,
        timeframe: str,
        candles: List[Candle],
        engine_id: str,
        trade_id: Optional[int] = None,
    ) -> None:
        self.queue.put(
            (
                self.repository.insert_candles_historical,
                (
                    symbol,
                    timeframe,
                    candles,
                    engine_id,
                    trade_id,
                    ),
                {},
            )
        )

    def insert_trade_historical(
        self,
        id: int,
        symbol: str,
        open_time: datetime,
        engine_id: str,
        candle_action: CandleAction,
        reason: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        volume: float,
        profit: float,
    ) -> None:
        self.queue.put(
            (
                self.repository.insert_trade_historical,
                (
                    id,
                    symbol,
                    open_time,
                    engine_id,
                    candle_action,
                    reason,
                    entry_price,
                    stop_loss,
                    take_profit,
                    volume,
                    profit,
                ),
                {},
            )
        )

    def insert_log(
        self,
        created_at: datetime,
        log_level: str,
        service_name: str,
        log_string: str,
    ) -> None:
        self.queue.put(
        (
            self.repository.insert_log,
            (
                created_at,
                log_level,
                service_name,
                log_string,
                ),
            {},
        )
    )

    def truncate_historical_tables(self) -> None:
        pass

    def shutdown(self, timeout: float = 5.0):
        self.queue.join()
        self.running = False
        self.queue.put(None)
        self.worker.join(timeout=timeout)
