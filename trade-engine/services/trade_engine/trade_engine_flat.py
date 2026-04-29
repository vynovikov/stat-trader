from typing import List, cast
from logging import LoggerAdapter

from statemachine import State, StateMachine
from datetime import datetime, timedelta

from domain.constants.constants import Constants
from domain.models.decision import Decision
from domain.models.order import Order
from domain.models.report import Report
from domain.models.trade_unit import Trade_unit
from domain.models.TPSL import TPSL
from domain.types.candle_action import CandleAction
from domain.types.candle import Candle
from domain.types.market_action import MarketAction
from domain.types.entrypoint import Entrypoint
from services.metric_repository.interface import MetricRepository
from services.counter_operator.interface import CounterOperator
from services.parameters_store.interface import ParametersStore
from services.history_operator.interface import HistoryOperator
from services.report_operator.interface import ReportOperator
from services.repository.interface import Repository
from services.bookkeeper.interface import Bookkeeper
from services.strategy_operator.interface_flat import StrategyOperatorFlat
from services.window_operator.interface import WindowOperator
from services.trade_engine.interface import TradeEngine
from services.log_operator.interface import LogOperator
from utils.time import utc_to_msk_string,utc_to_msk_datetime


@TradeEngine.register
class TradeEngineFlat(StateMachine):
    def __init__(
        self,
        repository: Repository,
        bookkeeper: Bookkeeper,
        strategy_operator: StrategyOperatorFlat,
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
        self.bookkeeper = bookkeeper
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
    idle_inside = State()

    initial_lower_breakthrough = State()
    initial_upper_breakthrough = State()

    subsequent_lower_breakthrough = State()
    subsequent_upper_breakthrough = State()

    initial_on_full_off_uptrend = State()
    initial_on_full_off_downtrend = State()

    initial_on_full_on_uptrend = State()
    initial_on_full_on_downtrend = State()

    cooldown = State()

    # Transitions
    warmed_up = not_ready.to(idle_inside)

    cooled_down = cooldown.to(idle_inside)

    initial_lower_breakthrough_ts = idle_inside.to(initial_lower_breakthrough)
    initial_upper_breakthrough_ts = idle_inside.to(initial_upper_breakthrough)

    subsequent_lowper_breakthrough_ts = initial_on_full_off_uptrend.to(subsequent_lower_breakthrough)
    subsequent_upper_breakthrough_ts = initial_on_full_off_downtrend.to(subsequent_upper_breakthrough)

    entrypoint_uptrend_full = initial_lower_breakthrough.to(initial_on_full_off_uptrend)
    entrypoint_downtrend_full = initial_upper_breakthrough.to(initial_on_full_off_downtrend)

    orders_cancelled = initial_lower_breakthrough.to(idle_inside) | initial_upper_breakthrough.to(idle_inside)

    back_inside_uptrend_initial = initial_lower_breakthrough.to(initial_on_full_off_uptrend)
    back_inside_downtrend_initial = initial_upper_breakthrough.to(initial_on_full_off_downtrend)

    back_inside_uptrend_subsequent = subsequent_lower_breakthrough.to(initial_on_full_on_uptrend)
    back_inside_downtrend_subsequent = subsequent_upper_breakthrough.to(initial_on_full_on_downtrend)

    consolidate = (
        subsequent_lower_breakthrough.to(initial_on_full_on_uptrend) |
        subsequent_upper_breakthrough.to(initial_on_full_on_downtrend)
    )

    TP_triggered = (
        initial_on_full_off_uptrend.to(cooldown) |
        initial_on_full_off_downtrend.to(cooldown) |
        initial_on_full_on_uptrend.to(cooldown) |
        initial_on_full_on_downtrend.to(cooldown)
    )

    SL_triggered = (
        initial_on_full_off_uptrend.to(cooldown) |
        initial_on_full_off_downtrend.to(cooldown) |
        initial_on_full_on_uptrend.to(cooldown) |
        initial_on_full_on_downtrend.to(cooldown)
    )

    def on_enter_idle_inside(self):
        if self.last_state_id in [
            "initial_lower_breakthrough",
            "initial_upper_breakthrough",
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

    def on_enter_initial_lower_breakthrough(self):
        """
        Actions to perform when entering uptrend state.
        """
        last_five_candles = self.window_operator.last_n_candles(n=5)
        self.history_operator.set(last_five_candles)

        order = self.strategy_operator.initial_uptrend_order(
            candle=last_five_candles[-1],
            spread=self.parameters_store.spread(),
            deposit=self.parameters_store.deposit(),
            risk_per_trade=self.parameters_store.risk_per_full_trade(),
            partial_trade_multiplier=self.parameters_store.partial_trade_multiplier(),
            min_volume=self.parameters_store.min_volume(),
            safe_factor=self.parameters_store.safe_factor(),
            min_price_delta=self.parameters_store.min_price_delta(),
            higher_edge=self.parameters_store.higher_edge(),
            lower_edge=self.parameters_store.lower_edge(),
        )
        self.parameters_store.set_order(order=order)

    def on_enter_initial_upper_breakthrough(self):
        """
        Actions to perform when upper edge breakthrough.
        """

        last_candle=self.window_operator.last_n_candles(1)[-1]

        self.history_operator.add(last_candle)

        volume,sl,tp=self.strategy_operator.initial_params_downtrend(
            candle=last_candle,
            spread=self.parameters_store.spread(),
            deposit=self.parameters_store.deposit(),
            risk_per_trade=self.parameters_store.risk_per_full_trade(),
            partial_trade_multiplier=self.parameters_store.partial_trade_multiplier(),
            min_volume=self.parameters_store.min_volume(),
            safe_factor=self.parameters_store.safe_factor(),
            lower_edge=self.parameters_store.lower_edge(),
        )

        order = Order(
            action=CandleAction.SELL,
            time=last_candle.close_time - timedelta(minutes=5),
            entry=last_candle.close,
            volume=volume
        )

        tpsl=TPSL(
            volume=volume,
            sl=sl,
            tp=tp,
        )

        self.parameters_store.set_order(order=order)
        self.parameters_store.set_tpsl(tpsl=tpsl)

    def on_enter_initial_on_full_off_downtrend(self):
        last_two_candles=self.window_operator.last_n_candles(2)

        if (
            last_two_candles[0].is_UP() and
            last_two_candles[1].is_DOWN()  and
            last_two_candles[0].close > self.parameters_store.higher_edge()
        ):
            new_high=last_two_candles[0].close
            self.parameters_store.set_higher_edge(new_high)

    def on_enter_initial_on_full_on_downtrend(self):
        last_candle=self.window_operator.last_n_candles(1)[-1]

        self.history_operator.add(last_candle)

        order = self.strategy_operator.additional_downtrend_order(
            candle=last_candle,
            spread=self.parameters_store.spread(),
            deposit=self.parameters_store.deposit(),
            risk_per_trade=self.parameters_store.risk_per_full_trade(),
            partial_trade_multiplier=self.parameters_store.partial_trade_multiplier(),
            min_volume=self.parameters_store.min_volume(),
            safe_factor=self.parameters_store.safe_factor(),
            min_price_delta=self.parameters_store.min_price_delta(),
            higher_edge=self.parameters_store.higher_edge(),
            lower_edge=self.parameters_store.lower_edge(),
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
        self.parameters_store.tpsl_reset()

    def window_is_full(self) -> bool:
        """
        Check if the window is full.
        """
        return (
            self.window_operator.window_len() == self.parameters_store.window_maxlen()
        )

    def is_cooled_down(self) -> bool:
        """
        Check if the cooldown period has passed.
        """
        return self.counter_operator.cooldown_dec()

    def after_transition(self, event, source):
        last_open_time = (
                self.window_operator.last_n_candles(1)[0].open_time
            ).replace(
                second=0,
                microsecond=0,
            )

        if (
                self.current_state_value == "initial_lower_breakthrough"
                or self.current_state_value == "initial_upper_breakthrough"
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
        """
        Handle a new candle and make decisions based on the current state.
        """
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

            case "idle_inside":
                self.last_state_id = self.current_state_value

                entrypoint = self.strategy_operator.entrypoint(
                    candle=candle,
                    higher_edge=self.parameters_store.higher_edge(),
                    lower_edge=self.parameters_store.lower_edge(),
                    margin=self.parameters_store.margin(),
                    service_name=self.parameters_store.strategy_operator_service_name(),
                )



                match entrypoint:
                    case Entrypoint.BUY:
                        self.send(
                            "entrypoint_uptrend",
                        )

                    case Entrypoint.SELL:
                        self.history_operator.add(candle=candle)
                        self.send(
                            "entrypoint_downtrend_initial",
                        )

            case "cooldown":
                self.last_state_id = self.current_state_value
                is_cooldown_passed = self.counter_operator.cooldown_dec()

                if is_cooldown_passed:
                    self.send("cooled_down")


            case "initial_lower_breakthrough" | "initial_upper_breakthrough":
                self.last_state_id = self.current_state_value
                self.history_operator.add(candle)

                is_moved_back_uptrend = self.strategy_operator.is_moved_back_uptrend(
                    candle=candle,
                    lower_edge=self.parameters_store.lower_edge(),
                )

                is_moved_back_downtrend = self.strategy_operator.is_moved_back_downtrend(
                    candle=candle,
                    higher_edge=self.parameters_store.higher_edge(),
                )

                match True:

                    case _ if is_moved_back_uptrend:
                        self.send("back_inside_uptrend_initial")

                    case _ if is_moved_back_downtrend:
                        self.send("back_inside_downtrend_initial")

                    case _ if is_moved_back_downtrend:
                        self.send("back_inside_downtrend_initial")

            case "initial_on_full_off_downtrend":
                self.last_state_id = self.current_state_value
                self.history_operator.add(candle)

                is_sl_triggered_downtrend = self.strategy_operator.is_sl_triggered_downtrend(
                    SL=self.parameters_store.order().sl,
                    candle=candle,
                )

                is_tp_triggered_downtrend = self.strategy_operator.is_tp_triggered_downtrend(
                    TP=self.parameters_store.order().tp,
                    candle=candle,
                )

                is_higher_breakthrough = self.strategy_operator.is_higher_breakthrough(
                    candle=candle,
                    higher_edge=self.parameters_store.higher_edge(),
                )


                match True:
                    case _ if is_higher_breakthrough:
                        self.send("subsequent_upper_breakthrough_ts")

                    case _ if is_sl_triggered_downtrend:
                        self.send("SL_triggered")

                    case _ if is_tp_triggered_downtrend:
                        self.send("TP_triggered")

            case "subsequent_lower_breakthrough" | "subsequent_upper_breakthrough":
                self.last_state_id = self.current_state_value

                is_breakthrough_consolidated=self.strategy_operator.is_breakthrough_consolidated(
                    order = self.parameters_store.order(),
                    candle = candle,
                )

                match True:
                    case _ if is_breakthrough_consolidated:
                        self.send("consolidate")

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
            case "idle_inside" if self.last_state_id not in [
                #"idle_inside",
                "initial_lower_breakthrough",
                "initial_upper_breakthrough",
            ]:
                self.last_state_id = self.current_state_value

                is_higher_breakthrough=self.strategy_operator.is_higher_breakthrough(
                    candle=candle,
                    higher_edge=self.parameters_store.higher_edge(),
                )

                is_lower_breakthrough=self.strategy_operator.is_lower_breakthrough(
                    candle=candle,
                    lower_edge=self.parameters_store.lower_edge(),
                )

                match True:
                    case _ if is_higher_breakthrough:
                        self.send("initial_upper_breakthrough_ts")

                    case _ if is_lower_breakthrough:
                        self.send("initial_lower_breakthrough_ts")


        action = self.strategy_operator.action(
            cast(str,self.current_state_value), self.last_state_id
        )
        order = (
            self.parameters_store.order() if action != MarketAction.HOLD else Order()
        )
        tpsl = (
            self.parameters_store.tpsl() if action != MarketAction.HOLD else TPSL()
        )
        report = self.parameters_store.report()

        return Decision(
            engine_id=self.parameters_store.engine_service_name(),
            order=order,
            tpsl=tpsl,
            action=action,
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
