from typing import List, Tuple
from datetime import timedelta
from logging import LoggerAdapter

from domain.constants.constants import Constants
from domain.models.order import Order
from domain.models.TPSL import TPSL
from domain.types.candle import Candle
from domain.types.candle_action import CandleAction
from domain.types.direction import Direction
from domain.types.market_action import MarketAction
from domain.types.power import Power
from domain.types.background import Background
from domain.types.entrypoint import Entrypoint
from services.bookkeeper.interface import Bookkeeper
from services.strategy_operator.interface_flat import StrategyOperatorFlat
from services.metric_repository.interface import MetricRepository
from utils.time import utc_to_msk_string,utc_to_msk_datetime


class StrategyOperatorFlatImpl(StrategyOperatorFlat):
    def __init__(
            self,
            bookkeeper: Bookkeeper,
            metric_repository: MetricRepository,
            logger: LoggerAdapter,
            ) -> None:

        self.bookkeeper = bookkeeper
        self.metric_repository = metric_repository
        self.logger = logger

    def is_sl_triggered(
        self,
        candle_action: CandleAction,
        SL: float,
        candle: Candle,
        ) -> bool:

        return candle.low<=SL if candle_action == CandleAction.BUY else candle.high >= SL

    def is_tp_triggered(
        self,
        candle_action: CandleAction,
        TP: float,
        candle: Candle,
        ) -> bool:

        return candle.high>TP if candle_action == CandleAction.BUY else candle.low < TP

    def price_difference(
            self,
            candle: Candle,
            order:Order,
            tpsl: TPSL,
            ) -> float:
        match order.action:
            case CandleAction.BUY if self.is_sl_triggered(order.action, tpsl.sl, candle):
                price_difference = tpsl.sl - order.entry
            case CandleAction.BUY if self.is_tp_triggered(order.action,tpsl.tp, candle):
                price_difference = tpsl.tp - order.entry
            case CandleAction.SELL if self.is_sl_triggered(order.action,tpsl.sl, candle):
                price_difference = order.entry - tpsl.sl
            case CandleAction.SELL if self.is_tp_triggered(order.action,tpsl.tp, candle):
                price_difference = order.entry - tpsl.tp
            case _:
                price_difference = 0.0

        return price_difference

    def on_market_profit(
        self,
        candle: Candle,
        order: Order,
        tpsl: TPSL,
    ) -> Tuple[float, float]:
        price_difference = self.price_difference(candle=candle,order=order,tpsl=tpsl)

        total_profit = self.bookkeeper.profit(
            price_difference=price_difference,
            volume=order.volume,
        )

        return price_difference, total_profit

    def off_market_profit(self, candle: Candle, direction: Direction) -> float:
        match direction:
            case Direction.UP:
                return candle.open - candle.close
            case Direction.DOWN:
                return candle.close - candle.open
            case _:
                return 0.0

    def risk(self, candles: List[Candle], direction: Direction) -> float:
        risk: float = 0.0

        match direction:
            case Direction.UP:
                risk = candles[-1].close - candles[-1].low
            case Direction.DOWN:
                risk = candles[-1].high - candles[-1].close

        return risk

    def profit_risk_ratio(self, profit: float, risk: float) -> float:
        if risk == 0:
            return 500

        return 100 * profit / risk

    def check_sl(self, order: Order, candle: Candle, spread: float) -> bool:
        match order.action:
            case CandleAction.BUY:
                return candle.low - spread <= order.sl
            case CandleAction.SELL:
                return candle.high + spread >= order.sl
            case _:
                return False

    def reason(
        self,
        order: Order,
        tpsl: TPSL,
        price_change: float,
        is_cancelled: bool,
        ) -> str:
        order_loss = abs(order.entry - tpsl.sl)

        match order.action:
            case CandleAction.BUY if is_cancelled:
                return Constants.BUY_CANCEL

            case CandleAction.BUY if price_change > 0:
                return Constants.BUY_TP

            case CandleAction.BUY if price_change <= 0 and abs(price_change) < order_loss:
                return Constants.BUY_LOSS

            case CandleAction.BUY if (
                price_change <= 0 and abs(price_change) == order_loss
            ):
                return Constants.BUY_SL

            case CandleAction.SELL if is_cancelled == True:
                return Constants.SELL_CANCEL

            case CandleAction.SELL if price_change > 0:
                return Constants.SELL_TP

            case CandleAction.SELL if (
                price_change <= 0 and abs(price_change) < order_loss
            ):
                return Constants.SELL_LOSS

            case CandleAction.SELL if (
                price_change <= 0 and abs(price_change) == order_loss
            ):
                return Constants.SELL_SL

            case _:
                return "Reason is not set"

    def action(
            self,
            current_state_id: str,
            last_state_id: str,
            background: Background,
            ) -> MarketAction:
            match (current_state_id,background):
                case ("initial_upper_breakthrough" | "upper_consolidation" ,b) if b<=0:
                    return MarketAction.OPEN

                case ("initial_lower_breakthrough" | "lower_consolidation",b) if b>=0:
                    return MarketAction.OPEN

                case ("cooldown",_) if last_state_id in [
                    "on_market_uptrend",
                    "on_market_downtrend",
                ]:
                    return MarketAction.CLOSE

                case _:
                    return MarketAction.HOLD

    def entrypoint(
        self,
        candle: Candle,
        higher_edge: float,
        lower_edge: float,
        margin:float,
        service_name: str,
    ) -> Entrypoint:
        last_open_time = (
                candle.open_time
            ).replace(
                second=0,
                microsecond=0,
            )

        is_buy_entrypoint=self._is_buy_entrypoint(
                candle=candle,
                higher_edge=higher_edge,
                lower_edge=lower_edge,
                margin=margin,
            )

        is_sell_entrypoint=self._is_sell_entrypoint(
                candle=candle,
                higher_edge=higher_edge,
                lower_edge=lower_edge,
                margin=margin,
            )

        match True:
            case _ if is_buy_entrypoint:
                self.logger.info(
                    "%s | entrypoint.BUY",
                    utc_to_msk_string(last_open_time),
                )

                self.metric_repository.insert_log(
                    created_at=utc_to_msk_datetime(last_open_time),
                    log_level="info",
                    service_name=service_name,
                    log_string=f"entrypoint.BUY",
                )

                return Entrypoint.BUY

            case _ if is_sell_entrypoint:
                self.logger.info(
                    "%s | entrypoint.SELL",
                    utc_to_msk_string(last_open_time),
                )

                self.metric_repository.insert_log(
                    created_at=utc_to_msk_datetime(last_open_time),
                    log_level="info",
                    service_name=service_name,
                    log_string=f"entrypoint.SELL",
                )

                return Entrypoint.SELL


        return Entrypoint.UNKNOWN

    def _is_buy_entrypoint(
        self,
        candle: Candle,
        higher_edge: float,
        lower_edge: float,
        margin: float,
    ) -> bool:
        """
        Check if price below lower margin
        """
        lower_margin=lower_edge+(higher_edge-lower_edge)*margin


        return (
            candle.low<lower_edge
            and candle.close<lower_margin
        )

    def _is_sell_entrypoint(
        self,
        candle: Candle,
        higher_edge: float,
        lower_edge: float,
        margin: float,
    ) -> bool:
        """
        Check if price above higher margin
        """
        higher_margin=higher_edge-(higher_edge-lower_edge)*margin


        return (
            candle.high>higher_edge
            and candle.close>higher_margin
        )


    def is_entry_triggered(self, order: Order, candle: Candle) -> bool:
        is_triggered = False

        if (order.action == CandleAction.BUY and candle.low < order.entry) or (
            order.action == CandleAction.SELL and candle.high > order.entry
        ):
            is_triggered = True

        return is_triggered

    def is_reversal_candle(self, order: Order, candle: Candle) -> bool:
        is_reversal = False

        if (order.action == CandleAction.BUY and candle.close > candle.open) or (
            order.action == CandleAction.SELL and candle.close < candle.open
        ):
            is_reversal = True

        return is_reversal

    def history_candles_uptrend(self, candles: List[Candle]) -> List[Candle]:
        history_candles:List[Candle] =[]

        if candles[0].is_DOWN:
            history_candles.append((candles[0]))

        for candle in candles[1:]:
            history_candles.append(candle)

        return history_candles

    def history_candles_downtrend(self, candles: List[Candle]) -> List[Candle]:
        history_candles:List[Candle] =[]

        if candles[0].is_UP:
            history_candles.append((candles[0]))

        for candle in candles[1:]:
            history_candles.append(candle)

        return history_candles

    def is_moved_back_uptrend(
        self,
        candle: Candle,
        lower_edge:float,
        ) -> bool:

        return (
            candle.is_UP() and
            candle.low<lower_edge and
            candle.close>lower_edge
        )

    def is_moved_back_downtrend(
        self,
        candle: Candle,
        higher_edge:float,
        ) -> bool:

        return (
            candle.is_DOWN() and
            candle.high>higher_edge and
            candle.close<higher_edge
        )

    def is_higher_breakthrough(
        self,
        candle: Candle,
        higher_edge:float,
        ) -> bool:

        return (
            candle.is_UP() and
            candle.close>=higher_edge
        )

    def is_lower_breakthrough(
        self,
        candle: Candle,
        lower_edge:float,
        ) -> bool:

        return (
            candle.is_DOWN() and
            candle.close<=lower_edge
        )

    def is_consolidated_lower(
        self,
        candle: Candle,
        lower_edge:float,
        higher_edge:float,
        margin: float,
        ) -> bool:

        edge = lower_edge - (higher_edge-lower_edge)*margin

        return (
            candle.is_DOWN() and
            candle.close<edge
        )

    def is_consolidated_higher(
        self,
        candle: Candle,
        lower_edge:float,
        higher_edge:float,
        margin: float,
        ) -> bool:

        edge = higher_edge + (higher_edge-lower_edge)*margin

        return (
            candle.is_UP() and
            candle.close>edge
        )

    def is_breakthrough_consolidated(
        self,
        order: Order,
        candle: Candle,
        ) -> bool:

        match True:
            case _ if (
                order.action==CandleAction.SELL and
                candle.is_UP() and
                candle.open>order.entry
            ):
                return True

            case _ if (
                order.action==CandleAction.BUY and
                candle.is_DOWN() and
                candle.open<order.entry
            ):
                return True

        return False

    def is_order_triggered(
        self,
        order: Order,
        candle: Candle,
    ) -> bool:

        match order.action:

            case CandleAction.SELL if candle.high>order.entry:
                return True

            case CandleAction.BUY if candle.low<order.entry:
                return True

        return False

    def initial_params_downtrend(
        self,
        candle: Candle,
        spread: float,
        deposit: float,
        risk_per_trade: float,
        partial_trade_multiplier: float,
        min_volume: float,
        safe_factor: float,
        lower_edge:float,
    ) -> Tuple[float,float,float]:
        calculated_tp = lower_edge + spread

        calculated_sl = candle.close + (candle.close-calculated_tp) - spread

        volume= self.bookkeeper.calculate_volume(
            entry_price=candle.close,
            sl=calculated_sl,
            deposit=deposit,
            risk_per_trade=risk_per_trade,
            partial_trade_multiplier=partial_trade_multiplier,
            min_volume=min_volume,
            safe_factor=safe_factor,
        )

        return volume,calculated_sl,calculated_tp

    def subsequent_params_downtrend(
        self,
        candle: Candle,
        spread: float,
        deposit: float,
        risk_per_trade: float,
        partial_trade_multiplier: float,
        min_volume: float,
        safe_factor: float,
        lower_edge:float,
    ) -> Tuple[float,float,float]:
        calculated_tp = lower_edge + spread

        calculated_sl = candle.high + (candle.high-calculated_tp)/2 - spread

        volume= self.bookkeeper.calculate_volume(
            entry_price=candle.high,
            sl=calculated_sl,
            deposit=deposit,
            risk_per_trade=risk_per_trade,
            partial_trade_multiplier=partial_trade_multiplier,
            min_volume=min_volume,
            safe_factor=safe_factor,
        )

        return volume,calculated_sl,calculated_tp

    def initial_params_uptrend(
        self,
        candle: Candle,
        spread: float,
        deposit: float,
        risk_per_trade: float,
        partial_trade_multiplier: float,
        min_volume: float,
        safe_factor: float,
        higher_edge:float,
    ) -> Tuple[float,float,float]:
        calculated_tp = higher_edge - spread

        calculated_sl = candle.close - (calculated_tp-candle.close) + spread

        volume= self.bookkeeper.calculate_volume(
            entry_price=candle.close,
            sl=calculated_sl,
            deposit=deposit,
            risk_per_trade=risk_per_trade,
            partial_trade_multiplier=partial_trade_multiplier,
            min_volume=min_volume,
            safe_factor=safe_factor,
        )

        return volume,calculated_sl,calculated_tp

    def subsequent_params_uptrend(
        self,
        candle: Candle,
        spread: float,
        deposit: float,
        risk_per_trade: float,
        partial_trade_multiplier: float,
        min_volume: float,
        safe_factor: float,
        higher_edge:float,
    ) -> Tuple[float,float,float]:
        calculated_tp = higher_edge - spread

        calculated_sl = candle.low - (calculated_tp-candle.low)/2 - spread

        volume= self.bookkeeper.calculate_volume(
            entry_price=candle.low,
            sl=calculated_sl,
            deposit=deposit,
            risk_per_trade=risk_per_trade,
            partial_trade_multiplier=partial_trade_multiplier,
            min_volume=min_volume,
            safe_factor=safe_factor,
        )

        return volume,calculated_sl,calculated_tp

    def is_codirectional(
        self,
        state: str,
        background: Background,
    ) -> bool:

        return (
          (state == "initial_upper_breakthrough" and background<=0) or
          (state == "initial_lower_breakthrough" and background>=0) or
          (state == "upper_consolidation" and background<=0) or
          (state == "initial_lower_breakthrough" and background>=0)
        )
