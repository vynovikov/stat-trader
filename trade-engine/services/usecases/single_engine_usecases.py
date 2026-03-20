from typing import List

from domain.models.decision import Decision
from domain.models.trade_unit import Trade_unit
from domain.types.candle import Candle
from domain.types.market_action import MarketAction

from services.usecases.interface import Usecases
from services.trade_engine.interface import TradeEngine
from services.metric_repository.interface import MetricRepository


class SingleEngineUsecases(Usecases):
    def __init__(
        self,
        trade_engine: TradeEngine,
        metric_repository: MetricRepository,
    ) -> None:
        self.trade_id: int = 1
        self.trade_engine = trade_engine
        self.metric_repository = metric_repository

    def _shorten_candles(
        self,
        candles: List[Candle],
    ) -> List[str]:
        result: List[str] = []

        for candle in candles:
            result.append("UP") if candle.close > candle.open else result.append("DOWN")

        return result

    def decide(
        self,
        trade_unit: Trade_unit,
    ) -> Decision:
        decision = self.trade_engine.handle_first(trade_unit)

        self.metric_repository.insert_candles_real(
            symbol="BTCUSDT",
            timeframe="5m",
            candles=[trade_unit.candle],
            engine_id=decision.engine_id,
            trade_id=0,
        )

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

            self.trade_id += 1

        print(
            f"[usecases] window: [{self._shorten_candles(self.trade_engine.window())}], cooldown: {self.trade_engine.get_cooldown()}"
        )
        print(f"[usecases] decision.action: {decision.action}")

        if decision.action != MarketAction.HOLD:
            print(f"[usecases] decision.order: {decision.order}")
            print(f"[usecases] profit: {decision.report.profit}")

        if decision.action == MarketAction.CLOSE:
            self.trade_engine.report_reset()

        return decision
