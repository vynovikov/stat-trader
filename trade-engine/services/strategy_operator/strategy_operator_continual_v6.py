from typing import List, Tuple
from datetime import timedelta
from logging import LoggerAdapter

from domain.constants.constants import Constants
from domain.models.order import Order
from domain.types.candle import Candle
from domain.types.candle_action import CandleAction
from domain.types.direction import Direction
from domain.types.market_action import MarketAction
from domain.types.background import Background
from domain.types.power import Power
from domain.types.entrypoint import Entrypoint
from services.bookkeeper.interface import Bookkeeper
from services.strategy_operator.interface import StrategyOperator
from services.metric_repository.interface import MetricRepository
from utils.time import utc_to_msk_string, utc_to_msk_datetime


class StrategyOperatorContinualV6(StrategyOperator):
    def __init__(
            self,
            bookkeeper: Bookkeeper,
            metric_repository: MetricRepository,
            logger: LoggerAdapter,
            ) -> None:

        self.bookkeeper = bookkeeper
        self.metric_repository = metric_repository
        self.logger = logger

    def uptrend_order(
        self,
        candle: Candle,
        history_candles: List[Candle],
        spread: float,
        deposit: float,
        risk_per_trade: float,
        min_volume: float,
        safe_factor: float,
        min_price_delta: float,
        power: Power,
    ) -> Order:
        candle_body = abs(candle.close - candle.open)

        calculated_entry = candle.close - min(
            candle.close + candle_body / 10, 2 * min_price_delta
        )

        calculated_sl = self._lowest_low(history_candles,candle) - spread
        calculated_sl_delta = calculated_entry - calculated_sl

        canculated_tp = calculated_entry + power.value * calculated_sl_delta

        order = Order(
            action=CandleAction.BUY,
            time=candle.close_time - timedelta(minutes=5),
            entry=calculated_entry,
            sl=calculated_sl,
            tp=canculated_tp,
            volume=self.bookkeeper.calculate_volume(
                entry_price=candle.close,
                sl=calculated_sl,
                deposit=deposit,
                risk_per_trade=risk_per_trade,
                min_volume=min_volume,
                safe_factor=safe_factor,
            ),
        )

        return order

    def downtrend_order(
        self,
        candle: Candle,
        history_candles: List[Candle],
        spread: float,
        deposit: float,
        risk_per_trade: float,
        min_volume: float,
        safe_factor: float,
        min_price_delta: float,
        power: Power,
    ) -> Order:
        candle_body = abs(candle.close - candle.open)

        calculated_entry = candle.close + min(
            candle.close + candle_body / 10, 2 * min_price_delta
        )

        calculated_sl = self._highest_high(history_candles,candle) - spread
        calculated_sl_delta = calculated_sl - calculated_entry

        canculated_tp = calculated_entry - power.value * calculated_sl_delta

        order = Order(
            action=CandleAction.SELL,
            time=candle.close_time - timedelta(minutes=5),
            entry=calculated_entry,
            sl=calculated_sl,
            tp=canculated_tp,
            volume=self.bookkeeper.calculate_volume(
                entry_price=candle.close,
                sl=calculated_sl,
                deposit=deposit,
                risk_per_trade=risk_per_trade,
                min_volume=min_volume,
                safe_factor=safe_factor,
            ),
        )

        return order

    def is_sl_triggered(self, order: Order, candle: Candle) -> bool:
        is_triggered = False

        if (order.action == CandleAction.BUY and candle.low <= order.sl) or (
            order.action == CandleAction.SELL and candle.high >= order.sl
        ):
            is_triggered = True

        return is_triggered

    def is_tp_triggered(self, order: Order, candle: Candle) -> bool:
        is_triggered = False

        if (order.action == CandleAction.BUY and candle.high > order.tp) or (
            order.action == CandleAction.SELL and candle.low < order.tp
        ):
            is_triggered = True

        return is_triggered

    def price_difference(self, order: Order, candle: Candle, spread: float) -> float:
        match order.action:
            case CandleAction.BUY if self.is_sl_triggered(order, candle):
                price_difference = order.sl - order.entry
            case CandleAction.BUY if self.is_tp_triggered(order, candle):
                price_difference = order.tp - order.entry
            case CandleAction.SELL if self.is_sl_triggered(order, candle):
                price_difference = order.entry - order.sl
            case CandleAction.SELL if self.is_tp_triggered(order, candle):
                price_difference = order.entry - order.tp
            case _:
                price_difference = 0.0

        return price_difference

    def on_market_profit(
        self, order: Order, candle: Candle, spread: float
    ) -> Tuple[float, float]:
        price_difference = self.price_difference(order, candle, spread)

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

    def reason(self, order: Order, price_change: float, is_cancelled: bool) -> str:
        order_sl = abs(order.entry - order.sl)

        match order.action:
            case CandleAction.BUY if is_cancelled:
                return Constants.BUY_CANCEL

            case CandleAction.BUY if price_change > 0:
                return Constants.BUY_TP

            case CandleAction.BUY if price_change <= 0 and abs(price_change) < order_sl:
                return Constants.BUY_LOSS

            case CandleAction.BUY if (
                price_change <= 0 and abs(price_change) == order_sl
            ):
                return Constants.BUY_SL

            case CandleAction.SELL if is_cancelled == True:
                return Constants.SELL_CANCEL

            case CandleAction.SELL if price_change > 0:
                return Constants.SELL_TP

            case CandleAction.SELL if (
                price_change <= 0 and abs(price_change) < order_sl
            ):
                return Constants.SELL_LOSS

            case CandleAction.SELL if (
                price_change <= 0 and abs(price_change) == order_sl
            ):
                return Constants.SELL_SL

            case _:
                return "Reason is not set"

    def action(self, current_state_id: str, last_state_id: str) -> MarketAction:
        match current_state_id:
            case "orders_uptrend" | "orders_downtrend":
                return MarketAction.OPEN

            case "cooldown" if last_state_id in [
                "on_market_uptrend",
                "on_market_downtrend",
            ]:
                return MarketAction.CLOSE

            case _:
                return MarketAction.HOLD

    def entrypoint(
        self,
        candles: List[Candle],
        body_ratio: float,
        shadow_ratio: float,
        background: Background,
        service_name: str,
    ) -> Entrypoint:
        last_open_time = (
                candles[-1].open_time
            ).replace(
                second=0,
                microsecond=0,
            )

        is_buy_entrypoint=self._is_buy_entrypoint(
                candles=candles,
                body_ratio=body_ratio,
                shadow_ratio=shadow_ratio,
            )

        is_sell_entrypoint=self._is_sell_entrypoint(
                candles=candles,
                body_ratio=body_ratio,
                shadow_ratio=shadow_ratio,
            )

        match True:
            case _ if is_buy_entrypoint:
                self.logger.info(
                    "%s | entrypoint.BUY, background: %s",
                    utc_to_msk_string(last_open_time),
                    background.name,
                )

                self.metric_repository.insert_log(
                    created_at=utc_to_msk_datetime(last_open_time),
                    log_level="info",
                    service_name=service_name,
                    log_string=f"entrypoint.BUY, background: {background}",
                )

                if self._is_buy_allowed(background):
                    self.logger.info(
                        "%s | entrypoint.BUY allowed",
                        utc_to_msk_string(last_open_time),
                    )

                    self.metric_repository.insert_log(
                        created_at=utc_to_msk_datetime(last_open_time),
                        log_level="warning",
                        service_name=service_name,
                        log_string=f"entrypoint.BUY allowed",
                    )

                    return Entrypoint.BUY

            case _ if is_sell_entrypoint:
                self.logger.info(
                    "%s | entrypoint.SELL, background: %s",
                    utc_to_msk_string(last_open_time),
                    background.name,
                )

                self.metric_repository.insert_log(
                    created_at=utc_to_msk_datetime(last_open_time),
                    log_level="info",
                    service_name=service_name,
                    log_string=f"entrypoint.SELL, background: {background}",
                )

                if self._is_sell_allowed(background):
                    self.logger.info(
                        "%s | entrypoint.SELL allowed",
                        utc_to_msk_string(last_open_time),
                    )

                    self.metric_repository.insert_log(
                        created_at=utc_to_msk_datetime(last_open_time),
                        log_level="warning",
                        service_name=service_name,
                        log_string=f"entrypoint.SELL allowed",
                    )

                    return Entrypoint.SELL


        return Entrypoint.UNKNOWN

    def _is_buy_entrypoint(
        self,
        candles: List[Candle],
        body_ratio: float,
        shadow_ratio: float,
    ) -> bool:
        """
        Check if a downtrend has started based on the last four candles.
        """
        if len(candles) < 5:
            return False

        patterns: List[bool] = []

        pattern0 = (
            candles[0].is_DOWN()
            and candles[1].is_UP()
            and candles[2].is_UP()
            and candles[3].is_UP()
            and candles[4].is_UP()
        )

        pattern1 = (
            candles[0].is_UP()
            and candles[1].is_DOWN()
            and (
                candles[2].is_UP()
                and candles[2].engulfs(candles[1], body_ratio, shadow_ratio)
            )
            and candles[3].is_UP()
            and candles[4].is_UP()
        )

        pattern2 = (
            candles[0].is_UP()
            and candles[1].is_UP()
            and candles[2].is_DOWN()
            and (
                candles[3].is_UP()
                and candles[3].engulfs(candles[2], body_ratio, shadow_ratio)
            )
            and candles[4].is_UP()
        )

        pattern3 = (
            candles[0].is_UP()
            and candles[1].is_UP()
            and candles[2].is_UP()
            and candles[3].is_DOWN()
            and (
                candles[4].is_UP()
                and candles[4].engulfs(candles[3], body_ratio, shadow_ratio)
            )
        )

        pattern4 = (
            candles[0].is_UP()
            and candles[1].is_UP()
            and candles[2].is_UP()
            and candles[3].is_UP()
            and candles[4].is_UP()
        )

        patterns.extend([pattern0, pattern1, pattern2, pattern3, pattern4])

        return True in patterns

    def _is_sell_entrypoint(
        self,
        candles: List[Candle],
        body_ratio: float,
        shadow_ratio: float,
    ) -> bool:
        """
        Check if an uptrend has started based on the last four candles.
        """
        if len(candles) < 5:
            return False

        patterns: List[bool] = []

        pattern0 = (
            candles[0].is_UP()
            and candles[1].is_DOWN()
            and candles[2].is_DOWN()
            and candles[3].is_DOWN()
            and candles[4].is_DOWN()
        )

        pattern1 = (
            candles[0].is_DOWN()
            and candles[1].is_UP()
            and (
                candles[2].is_DOWN()
                and candles[2].engulfs(candles[1], body_ratio, shadow_ratio)
            )
            and candles[3].is_DOWN()
            and candles[4].is_DOWN()
        )

        pattern2 = (
            candles[0].is_DOWN()
            and candles[1].is_DOWN()
            and candles[2].is_UP()
            and (
                candles[3].is_DOWN()
                and candles[3].engulfs(candles[2], body_ratio, shadow_ratio)
            )
            and candles[4].is_DOWN()
        )

        pattern3 = (
            candles[0].is_DOWN()
            and candles[1].is_DOWN()
            and candles[2].is_DOWN()
            and candles[3].is_UP()
            and (
                candles[4].is_DOWN()
                and candles[4].engulfs(candles[3], body_ratio, shadow_ratio)
            )
        )

        pattern4 = (
            candles[0].is_DOWN()
            and candles[1].is_DOWN()
            and candles[2].is_DOWN()
            and candles[3].is_DOWN()
            and candles[4].is_DOWN()
        )

        patterns.extend([pattern0, pattern1, pattern2, pattern3, pattern4])

        return True in patterns

    def _is_buy_allowed(
            self,
            background: Background,
            ) ->bool:

        return background in [Background.BULLISH_CON,Background.BULLISH_CON_REV]

    def _is_sell_allowed(
            self,
            background: Background,
            ) ->bool:

        return background in [Background.BEARISH_CON, Background.BEARISH_CON_REV]

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

    def _highest_high(self, history_candles: List[Candle], candle: Candle) -> float:
        if len(history_candles)<1 or history_candles[0].high<=0 or candle.high<=0:
            return -1

        highest_high=history_candles[0].high

        for history_candle in history_candles[1:]:

            if history_candle.high<=0:
                return -1

            if history_candle.high>highest_high:
                highest_high=history_candle.high

        if candle.high>highest_high:
            highest_high=candle.high


        return highest_high

    def _lowest_low(self, history_candles: List[Candle], candle: Candle) -> float:
        if len(history_candles)<1 or history_candles[0].low<=0 or candle.low<=0:
            return -1

        lowest_low=history_candles[0].low

        for history_candle in history_candles[1:]:

            if history_candle.low<=0:
                return -1

            if history_candle.low<lowest_low:
                lowest_low=history_candle.low

        if candle.low<lowest_low:
            lowest_low=candle.low


        return lowest_low

    def history_candles_uptrend(self, candles: List[Candle]) -> List[Candle]:
        history_candles:List[Candle] =[]

        if candles[0].is_UP:
            history_candles.append((candles[0]))

        for candle in candles[1:]:
            history_candles.append(candle)

        return history_candles

    def history_candles_downtrend(self, candles: List[Candle]) -> List[Candle]:
        history_candles:List[Candle] =[]

        if candles[0].is_DOWN:
            history_candles.append((candles[0]))

        for candle in candles[1:]:
            history_candles.append(candle)

        return history_candles
