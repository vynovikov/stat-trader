import os
import sys

# Получаем путь к текущему скрипту
current_dir = os.path.dirname(os.path.abspath(__file__))

# Поднимаемся на два уровня выше, чтобы попасть в корневой каталог проекта (ml-agent)
# Путь может быть другим, в зависимости от того, где находится config.py
project_root = os.path.abspath(os.path.join(current_dir, "../../"))

# Добавляем корневой каталог в sys.path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sqlalchemy import Table, Column, MetaData, String, Float, Integer, DateTime, insert
from sqlalchemy.dialects import mysql
from datetime import datetime
from typing import List, Optional

import clickhouse_connect

from domain.types.candle import Candle
from domain.types.candle_action import CandleAction
from services.metric_repository.interface import MetricRepository


class ClickhouseMetricRepository(MetricRepository):
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        database: str,
    ) -> None:
        self.client = clickhouse_connect.get_client(
            host=host,
            port=port,
            username=username,
            password=password,
            database=database,
        )

        self.metadata = MetaData()

        self.trades_real_table = Table(
            "trades_real",
            self.metadata,
            Column("id", Integer),
            Column("symbol", String),
            Column("open_time", DateTime),
            Column("engine_id", String),
            Column("candle_action", String),
            Column("reason", String),
            Column("entry_price", Float),
            Column("stop_loss", Float),
            Column("take_profit", Float),
            Column("volume", Float),
            Column("profit", Float),
        )

        self.candles_all_table = Table(
            "candles_all",
            self.metadata,
            Column("symbol", String),
            Column("timeframe", String),
            Column("open", Float),
            Column("high", Float),
            Column("low", Float),
            Column("close", Float),
            Column("open_time", DateTime),
            Column("close_time", DateTime),
            Column("volume", Float),
        )

        self.candles_traded_table = Table(
            "candles_traded",
            self.metadata,
            Column("symbol", String),
            Column("timeframe", String),
            Column("engine_id", String),
            Column("open", Float),
            Column("high", Float),
            Column("low", Float),
            Column("close", Float),
            Column("open_time", DateTime),
            Column("close_time", DateTime),
            Column("volume", Float),
            Column("trade_id", Integer, nullable=True),
        )

        self.trades_historical_table = Table(
            "trades_historical",
            self.metadata,
            Column("id", Integer),
            Column("symbol", String),
            Column("open_time", DateTime),
            Column("engine_id", String),
            Column("candle_action", String),
            Column("reason", String),
            Column("entry_price", Float),
            Column("stop_loss", Float),
            Column("take_profit", Float),
            Column("volume", Float),
            Column("profit", Float),
        )

        self.candles_historical_table = Table(
            "candles_historical",
            self.metadata,
            Column("symbol", String),
            Column("timeframe", String),
            Column("engine_id", String),
            Column("open", Float),
            Column("high", Float),
            Column("low", Float),
            Column("close", Float),
            Column("open_time", DateTime),
            Column("close_time", DateTime),
            Column("volume", Float),
            Column("trade_id", Integer, nullable=True),
        )

        self.logs_table = Table(
            "logs",
            self.metadata,
            Column("created_at", DateTime),
            Column("log_level", String),
            Column("service_name", String),
            Column("log_string", String),
        )

        self.dialect = mysql.dialect(paramstyle="pyformat")

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
        stmt = insert(self.trades_real_table).values(
            id=id,
            symbol=symbol,
            open_time=open_time,
            engine_id=engine_id,
            candle_action=candle_action.value,
            reason=reason,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            volume=volume,
            profit=profit,
        )

        compiled = stmt.compile(dialect=self.dialect)
        sql_str = str(compiled)
        params = dict(compiled.params)

        self.client.query(sql_str, parameters=params)

    def insert_candles_all(
        self,
        symbol: str,
        timeframe: str,
        candles: List[Candle],
    ) -> None:
        if not candles:
            return

        values_list = []
        for candle in candles:
            values_list.append(
                {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "open": candle.open,
                    "high": candle.high,
                    "low": candle.low,
                    "close": candle.close,
                    "open_time": candle.open_time,
                    "close_time": candle.close_time,
                    "volume": candle.volume,
                }
            )

        stmt = insert(self.candles_all_table).values(values_list)

        compiled = stmt.compile(dialect=self.dialect)
        sql_str = str(compiled)
        params = dict(compiled.params)

        self.client.query(sql_str, parameters=params)

    def insert_candles_traded(
        self,
        symbol: str,
        timeframe: str,
        candles: List[Candle],
        engine_id: str,
        trade_id: Optional[int] = None,
    ) -> None:
        if not candles:
            return

        values_list = []
        for candle in candles:
            values_list.append(
                {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "engine_id": engine_id,
                    "open": candle.open,
                    "high": candle.high,
                    "low": candle.low,
                    "close": candle.close,
                    "open_time": candle.open_time,
                    "close_time": candle.close_time,
                    "volume": candle.volume,
                    "trade_id": trade_id,
                }
            )

        stmt = insert(self.candles_traded_table).values(values_list)

        compiled = stmt.compile(dialect=self.dialect)
        sql_str = str(compiled)
        params = dict(compiled.params)

        self.client.query(sql_str, parameters=params)

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
        stmt = insert(self.trades_historical_table).values(
            id=id,
            symbol=symbol,
            open_time=open_time,
            engine_id=engine_id,
            candle_action=candle_action.value,
            reason=reason,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            volume=volume,
            profit=profit,
        )

        compiled = stmt.compile(dialect=self.dialect)
        sql_str = str(compiled)
        params = dict(compiled.params)

        self.client.query(sql_str, parameters=params)

    def insert_candles_historical(
        self,
        symbol: str,
        timeframe: str,
        candles: List[Candle],
        engine_id: str,
        trade_id: Optional[int] = None,
    ) -> None:
        if not candles:
            return

        values_list = []
        for candle in candles:
            values_list.append(
                {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "engine_id": engine_id,
                    "open": candle.open,
                    "high": candle.high,
                    "low": candle.low,
                    "close": candle.close,
                    "open_time": candle.open_time,
                    "close_time": candle.close_time,
                    "volume": candle.volume,
                    "trade_id": trade_id,
                }
            )

        stmt = insert(self.candles_historical_table).values(values_list)

        compiled = stmt.compile(dialect=self.dialect)
        sql_str = str(compiled)
        params = dict(compiled.params)

        self.client.query(sql_str, parameters=params)

    def insert_log(
        self,
        created_at: datetime,
        log_level: str,
        service_name: str,
        log_string: str,
    ) -> None:
        if not log_string:
            return

        values = {
            "created_at": created_at,
            "log_level": log_level,
            "service_name": service_name,
            "log_string": log_string,
        }

        stmt = insert(self.logs_table).values(values)

        compiled = stmt.compile(dialect=self.dialect)
        sql_str = str(compiled)
        params = dict(compiled.params)

        self.client.query(sql_str, parameters=params)

    def optimize(self) -> None:
        self.client.command("OPTIMIZE TABLE trades_real FINAL")
        self.client.command("OPTIMIZE TABLE candles_all FINAL")
        self.client.command("OPTIMIZE TABLE candles_traded FINAL")
        self.client.command("OPTIMIZE TABLE trades_historical FINAL")
        self.client.command("OPTIMIZE TABLE candles_historical FINAL")
        self.client.command("OPTIMIZE TABLE logs FINAL")

    def truncate_historical_tables(self) -> None:
        """Очищает все исторические таблицы (trades и candles)"""
        self.client.command("TRUNCATE TABLE trades_historical")
        self.client.command("TRUNCATE TABLE candles_historical")

    def truncate_real_tables(self) -> None:
        """Очищает все реалтайм таблицы (trades и candles)"""
        self.client.command("TRUNCATE TABLE trades_real")
        self.client.command("TRUNCATE TABLE candles_traded")
        self.client.command("TRUNCATE TABLE candles_all")

    def truncate_logs_tables(self) -> None:
        """Очищает таблицу логов"""
        self.client.command("TRUNCATE TABLE logs")

    def truncate_all_tables(self) -> None:
        """Очищает все таблицы метрик"""
        self.truncate_historical_tables()
        self.truncate_real_tables()
        self.truncate_logs_tables()


if __name__ == "__main__":
    repo = ClickhouseMetricRepository(
        host="localhost",
        port=8123,
        username="vt_user",
        password="vt_pass",
        database="default",
    )

    repo.insert_trade_historical(
        id=2,
        symbol="BTCUSD",
        open_time=datetime(2025, 1, 10, 13, 45, 0),
        engine_id="rev_v4",
        candle_action=CandleAction.SELL,
        reason="Stop Loss Hit",
        entry_price=10600.0,
        stop_loss=10650.0,
        take_profit=10000,
        volume=0.1,
        profit=-10,
    )

    candles = [
        Candle(
            high=10200.0,
            low=9950.0,
            open=10000.0,
            close=10150.0,
            close_time=datetime(2025, 1, 10, 13, 30, 0),
            volume=250.0,
        ),
        Candle(
            high=10350.0,
            low=10100.0,
            open=10150.0,
            close=10300.0,
            close_time=datetime(2025, 1, 10, 13, 35, 0),
            volume=300.0,
        ),
        Candle(
            high=10500.0,
            low=10250.0,
            open=10300.0,
            close=10450.0,
            close_time=datetime(2025, 1, 10, 13, 40, 0),
            volume=250.0,
        ),
        Candle(
            high=10650.0,
            low=10400.0,
            open=10450.0,
            close=10600.0,
            close_time=datetime(2025, 1, 10, 13, 45, 0),
            volume=300.0,
        ),
        Candle(
            high=10750.0,
            low=10550.0,
            open=10600.0,
            close=10700.0,
            close_time=datetime(2025, 1, 10, 13, 50, 0),
            volume=300.0,
        ),
    ]

    repo.insert_candles_historical(
        symbol="BTCUSD",
        timeframe="5m",
        engine_id="rev_v5",
        candles=candles,
        trade_id=2,
    )

    repo.optimize()
