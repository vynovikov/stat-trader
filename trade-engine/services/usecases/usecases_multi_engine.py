import logging

from typing import List
from logging import LoggerAdapter

from domain.models.order import Order
from domain.models.report import Report
from domain.models.decision import Decision
from domain.models.trade_unit import Trade_unit
from domain.types.candle import Candle
from domain.types.market_action import MarketAction

from services.usecases.interface import Usecases
from services.trade_engine.interface import TradeEngine
from services.metric_repository.interface import MetricRepository
from utils.time import utc_to_msk_string

def get_logger(label: str) -> LoggerAdapter:
    stream_handler = logging.StreamHandler()

    stream_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(logging_group)s] %(message)s")
    stream_handler.setFormatter(formatter)

    base_logger = logging.getLogger(label)
    base_logger.setLevel(logging.INFO)
    base_logger.addHandler(stream_handler)

    logger = logging.LoggerAdapter(base_logger, {"logging_group": label})

    return logger

class UsecasesMultiEngine(Usecases):
    def __init__(
        self,
        trade_engines: List[TradeEngine],
        metric_repository: MetricRepository,
        engage_engine_id:str ="",
    ) -> None:
        self.trade_id: int = 0
        self.trade_engines = trade_engines
        self.metric_repository = metric_repository
        self.engage_engine_id=engage_engine_id

        self.logger = get_logger("usecases")

    def _shorten_candles(
        self,
        candles: List[Candle],
    ) -> List[str]:
        result: List[str] = []

        for candle in candles:
            result.append("UP") if candle.close > candle.open else result.append("DOWN")

        return result

    def _get_decision(self,decisions: List[Decision]) -> Decision:
        for decision in decisions:

            match True:
                case _ if decision.action == MarketAction.OPEN and len(self.engage_engine_id)==0:
                    self.engage_engine_id=decision.engine_id

                    return decision

                case _ if decision.action == MarketAction.CLOSE and self.engage_engine_id==decision.engine_id:
                    self.engage_engine_id=""

                    return decision



        return Decision(
            engine_id="",
            order=Order(),
            action=MarketAction.HOLD,
            report=Report(),
        )

    def decide(
        self,
        trade_unit: Trade_unit,
    ) -> Decision:
        candle=trade_unit.candle

        self.metric_repository.insert_candles_all(
            symbol="BTCUSDT",
            timeframe="15m",
            candles=[candle],
        )

        decisions: List[Decision] =[]


        for trade_engine in self.trade_engines:
            decisions.append(trade_engine.handle_first(trade_unit))

        decision = self._get_decision(decisions)

        if decision.action == MarketAction.CLOSE:
            self.metric_repository.insert_trade_real(
                id=self.trade_id,
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

            self.metric_repository.insert_candles_traded(
            symbol="BTCUSDT",
            timeframe="15m",
            candles=decision.report.candles,
            engine_id=decision.engine_id,
            trade_id=self.trade_id,
        )

            self.trade_id += 1

        self.logger.info(
                    "%s | %s: ",
                    utc_to_msk_string(candle.open_time),
                    f"window: [{self._shorten_candles(self.trade_engines[0].window())}]"
                )

        self.logger.info(
                    "%s | %s: ",
                    utc_to_msk_string(candle.open_time),
                    f"decision.action: {decision.action}"
                )

        if decision.action != MarketAction.HOLD:
            self.logger.info(
                    "%s | %s: ",
                    utc_to_msk_string(candle.open_time),
                    f"decision.order: {decision.order}"
                )

            self.logger.info(
                    "%s | %s: ",
                    utc_to_msk_string(candle.open_time),
                    f"profit: {round(decision.report.profit,2)}"
                )

        if decision.action == MarketAction.CLOSE:

            for trade_engine in self.trade_engines:
                trade_engine.report_reset()

        return decision

    def reports_reset(self):
        for trade_engine in self.trade_engines:
            trade_engine.report_reset()
