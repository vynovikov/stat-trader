from typing import List, cast
from logging import LoggerAdapter

from statemachine import State, StateMachine
from datetime import datetime, timedelta

from domain.models.decision import Decision
from domain.models.order import Order
from domain.models.report import Report
from domain.models.trade_unit import Trade_unit
from domain.types.candle import Candle
from domain.types.market_action import MarketAction
from domain.types.entrypoint import Entrypoint
from services.metric_repository.interface import MetricRepository
from services.counter_operator.interface import CounterOperator
from services.parameters_store.interface import ParametersStore
from services.history_operator.interface import HistoryOperator
from services.report_operator.interface import ReportOperator
from services.repository.interface import Repository
from services.strategy_operator.interface import StrategyOperator
from services.window_operator.interface import WindowOperator
from services.trade_engine.interface import TradeEngine
from services.log_operator.interface import LogOperator
from utils.time import utc_to_msk_string,utc_to_msk_datetime


@TradeEngine.register
class TradeEngineContinualV6(StateMachine):
    def __init__(
        self,
        repository: Repository,
        strategy_operator: StrategyOperator,
        history_operator: HistoryOperator,
        window_operator: WindowOperator,
        counter_operator: CounterOperator,
        report_operator: ReportOperator,
        log_operator: LogOperator,
        parameters_store: ParametersStore,
        metric_repository: MetricRepository,
        logger: LoggerAdapter,
    ):
        self.strategy_operator = strategy_operator
        self.repository = repository
        self.window_operator = window_operator
        self.counter_operator = counter_operator
        self.parameters_store = parameters_store
        self.history_operator = history_operator
        self.report_operator = report_operator
        self.log_operator = log_operator
        self.last_state_id: str = "not_ready"
        self.metric_repository = metric_repository
        self.logger = logger

        super().__init__()

    # States
    not_ready = State(initial=True)
    idle = State()

    trigger_uptrend = State()
    trigger_downtrend = State()

    orders_uptrend = State()
    orders_downtrend = State()  # type: ignore

    on_market_uptrend = State()
    on_market_downtrend = State()

    cooldown = State()

    # Transitions
    warmed_up = not_ready.to(idle)

    cooled_down = cooldown.to(idle)

    entrypoint_uptrend = idle.to(trigger_uptrend)
    entrypoint_downtrend = idle.to(trigger_downtrend)

    triggered_uptrend = trigger_uptrend.to(orders_uptrend)
    triggered_downtrend = trigger_downtrend.to(orders_downtrend)  # type: ignore

    orders_cancelled = orders_uptrend.to(idle) | orders_downtrend.to(idle)

    entry_triggered = orders_uptrend.to(on_market_uptrend) | orders_downtrend.to(
        on_market_downtrend
    )

    TP_triggered = on_market_downtrend.to(cooldown) | on_market_uptrend.to(cooldown)
    SL_triggered = on_market_downtrend.to(cooldown) | on_market_uptrend.to(cooldown)

    def on_enter_idle(self):
        if self.last_state_id in [
            "orders_uptrend",
            "orders_downtrend",
        ]:
            order = self.parameters_store.order()

            report = self.report_operator.report(
                candles=self.history_operator.get(),
                order=order,
                reason=self.strategy_operator.reason(
                    order=order,
                    price_change=0,
                    is_cancelled=True,
                ),
                profit=0,
            )
            self.parameters_store.set_report(report=report)
            self.parameters_store.order_reset()
            self.history_operator.clear()

    def on_enter_trigger_uptrend(self):
        last_five_candles = self.window_operator.last_n_candles(n=5)

        history_candles=self.strategy_operator.history_candles_uptrend(last_five_candles)

        self.history_operator.set(history_candles)

    def on_enter_trigger_downtrend(self):
        last_five_candles = self.window_operator.last_n_candles(n=5)

        history_candles=self.strategy_operator.history_candles_downtrend(last_five_candles)

        self.history_operator.set(history_candles)

    def on_enter_orders_uptrend(self):
        last_candle = self.window_operator.last_n_candles(n=1)[0]
        history_candles=self.history_operator.get()

        order = self.strategy_operator.uptrend_order(
            candle=last_candle,
            history_candles=history_candles,
            spread=self.parameters_store.spread(),
            deposit=self.parameters_store.deposit(),
            risk_per_trade=self.parameters_store.risk_per_trade(),
            min_volume=self.parameters_store.min_volume(),
            safe_factor=self.parameters_store.safe_factor(),
            min_price_delta=self.parameters_store.min_price_delta(),
            power=self.parameters_store.power(),
        )
        self.parameters_store.set_order(order=order)

    def on_enter_orders_downtrend(self):
        last_candle = self.window_operator.last_n_candles(n=1)[0]
        history_candles=self.history_operator.get()

        order = self.strategy_operator.downtrend_order(
            candle=last_candle,
            history_candles=history_candles,
            spread=self.parameters_store.spread(),
            deposit=self.parameters_store.deposit(),
            risk_per_trade=self.parameters_store.risk_per_trade(),
            min_volume=self.parameters_store.min_volume(),
            safe_factor=self.parameters_store.safe_factor(),
            min_price_delta=self.parameters_store.min_price_delta(),
            power=self.parameters_store.power(),
        )
        self.parameters_store.set_order(order=order)

    def on_enter_cooldown(self):
        """
        Actions to perform when entering off_market cooldown state.
        """

        order = self.parameters_store.order()
        last_candle = self.window_operator.last_n_candles(n=1)
        history_candles = self.history_operator.get()

        old_deposit = self.parameters_store.deposit()
        price_change, deposit_change = self.strategy_operator.on_market_profit(
            order=order,
            candle=last_candle[0],
            spread=self.parameters_store.spread(),
        )

        reason = self.strategy_operator.reason(
            order=order,
            price_change=price_change,
            is_cancelled=False,
        )

        report = self.report_operator.report(
            candles=history_candles,
            order=order,
            reason=reason,
            profit=deposit_change,
        )

        self.parameters_store.set_report(report=report)
        self.parameters_store.set_deposit(deposit=old_deposit + deposit_change)

        self.history_operator.clear()
        self.counter_operator.cooldown_set()
        self.parameters_store.order_reset()

    def window_is_full(self) -> bool:

        return (
            self.window_operator.window_len() == self.parameters_store.window_maxlen()
        )

    def is_cooled_down(self) -> bool:

        return self.counter_operator.cooldown_dec()

    def after_transition(self, event, source):
        last_open_time = (
                self.window_operator.last_n_candles(1)[0].open_time
            ).replace(
                second=0,
                microsecond=0,
            )

        if (
                self.current_state_value == "trigger_uptrend"
                or self.current_state_value == "trigger_downtrend"
            ):

                trade_id = self.parameters_store.trade_id()
                trade_id += 1
                self.parameters_store.set_trade_id(trade_id)

        self.logger.info(
            "%s | cooldown %s: %s -> (%s) -> %s",
            utc_to_msk_string(last_open_time),
            self.counter_operator.cooldown_counter(),
            source.id,
            event,
            self.current_state_value,
        )

        log_level=self.log_operator.log_level(
            event=event,
        )

        log_string=self.log_operator.log_string(
            cooldown = self.counter_operator.cooldown_counter(),
            initial_state=source.id,
            event = event,
            final_state=cast(str,self.current_state_value),
        )

        self.metric_repository.insert_log(
            created_at=utc_to_msk_datetime(last_open_time),
            log_level=log_level,
            service_name=self.parameters_store.engine_service_name(),
            log_string=log_string
        )

    def handle_first(self, trade_unit: Trade_unit) -> Decision:

        self.window_operator.shift_window(candle=trade_unit.candle)
        self.parameters_store.set_deposit(deposit=trade_unit.deposit)
        self.parameters_store.set_spread(spread=trade_unit.spread)
        candle = trade_unit.candle

        close_time = (candle.close_time + timedelta(hours=3, seconds=1)).replace(
            second=0,
            microsecond=0,
        )

        match self.current_state_value:
            case "not_ready":
                self.last_state_id = self.current_state_value
                if (
                    len(self.window_operator.all_candles())
                    > self.parameters_store.window_maxlen() - 1
                ):
                    self.send("warmed_up")

            case "idle":
                self.last_state_id = self.current_state_value
                last_five_candles = self.window_operator.last_n_candles(n=5)
                background = self.parameters_store.background()

                entrypoint = self.strategy_operator.entrypoint(
                    candles=last_five_candles,
                    body_ratio=self.parameters_store.body_ratio(),
                    shadow_ratio=self.parameters_store.shadow_ratio(),
                    background=background,
                    service_name=self.parameters_store.strategy_operator_service_name(),
                )

                match entrypoint:
                    case Entrypoint.BUY:
                        self.send(
                            "entrypoint_uptrend",
                        )

                    case Entrypoint.SELL:
                        self.send(
                            "entrypoint_downtrend",
                        )

            case "cooldown":
                self.last_state_id = self.current_state_value
                is_cooldown_passed = self.counter_operator.cooldown_dec()

                if is_cooldown_passed:
                    self.send("cooled_down")

                return Decision(
                    engine_id=self.parameters_store.engine_service_name(),
                    action=MarketAction.HOLD,
                    order=Order(),
                    report=Report(),
                )

            case "trigger_uptrend":
                self.last_state_id = self.current_state_value
                self.history_operator.add(candle)

                if candle.is_DOWN():
                    self.send("triggered_uptrend")

            case "trigger_downtrend":
                self.last_state_id = self.current_state_value
                self.history_operator.add(candle)

                if candle.is_UP():
                    self.send("triggered_downtrend")

            case "orders_uptrend" | "orders_downtrend":
                self.last_state_id = self.current_state_value
                self.history_operator.add(candle)

                is_entry_triggered = self.strategy_operator.is_entry_triggered(
                    self.parameters_store.order(),
                    candle,
                )

                is_reversal_candle = self.strategy_operator.is_reversal_candle(
                    self.parameters_store.order(),
                    candle,
                )

                match True:
                    case _ if is_entry_triggered:
                        self.send("entry_triggered")

                    case _ if is_reversal_candle:
                        self.send("orders_cancelled")

            case "on_market_uptrend" | "on_market_downtrend":
                self.last_state_id = self.current_state_value
                self.history_operator.add(candle)

                is_sl_triggred = self.strategy_operator.is_sl_triggered(
                    order=self.parameters_store.order(),
                    candle=candle,
                )

                is_tp_triggered = self.strategy_operator.is_tp_triggered(
                    order=self.parameters_store.order(),
                    candle=candle,
                )

                match True:

                    case _ if is_sl_triggred == True:
                        self.send("SL_triggered")

                    case _ if is_tp_triggered == True:
                        self.send("TP_triggered")

        return self.handle_second(candle)

    def handle_second(self, candle: Candle) -> Decision:
        """
        Handle a new candle and make decisions based on the current state.
        """
        close_time = (candle.close_time + timedelta(hours=3, seconds=1)).replace(
            second=0,
            microsecond=0,
        )

        match self.current_state_value:
            case "idle" if self.last_state_id not in [
                "idle",
                "orders_uptrend",
                "orders_downtrend",
            ]:
                self.last_state_id = self.current_state_value
                last_five_candles = self.window_operator.last_n_candles(n=5)
                background = self.parameters_store.background()

                entrypoint = self.strategy_operator.entrypoint(
                    candles=last_five_candles,
                    body_ratio=self.parameters_store.body_ratio(),
                    shadow_ratio=self.parameters_store.shadow_ratio(),
                    background=background,
                    service_name=self.parameters_store.strategy_operator_service_name(),
                )

                match entrypoint:
                    case Entrypoint.BUY:
                        self.send(
                            "entrypoint_uptrend",
                        )

                    case Entrypoint.SELL:
                        self.send(
                            "entrypoint_downtrend",
                        )

            case "on_market_uptrend" | "on_market_downtrend":
                self.last_state_id = self.current_state_value

                is_sl_triggred = self.strategy_operator.is_sl_triggered(
                    order=self.parameters_store.order(),
                    candle=candle,
                )

                is_tp_triggered = self.strategy_operator.is_tp_triggered(
                    order=self.parameters_store.order(),
                    candle=candle,
                )

                match True:
                    case _ if is_sl_triggred == True:
                        self.send("SL_triggered")

                    case _ if is_tp_triggered == True:
                        self.send("TP_triggered")

        action = self.strategy_operator.action(
            cast(str,self.current_state_value), self.last_state_id
        )
        order = (
            self.parameters_store.order() if action != MarketAction.HOLD else Order()
        )
        report = self.parameters_store.report()

        return Decision(
            engine_id=self.parameters_store.engine_service_name(),
            action=action,
            order=order,
            report=report,
        )

    def deposit(self) -> float:
        return self.parameters_store.deposit()

    def window(self) -> List[Candle]:
        return self.window_operator.all_candles()

    def get_cooldown(self) -> int:
        return self.counter_operator.cooldown_counter()

    def report_reset(self) -> None:
        self.parameters_store.report_reset()

    def engine_id(self) -> str:
        return self.parameters_store.engine_service_name()
