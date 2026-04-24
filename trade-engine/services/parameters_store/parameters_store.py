from domain.models.order import Order
from domain.models.report import Report
from domain.types.payload import Payload
from domain.types.entrypoint import Entrypoint
from domain.types.background import Background
from domain.types.power import Power
from services.parameters_store.interface import ParametersStore


class ParametersStoreImpl(ParametersStore):
    def __init__(
        self,
        prelude_len: int,
        window_len: int,
        risk_per_full_trade: float,
        partial_trade_multiplier: float,
        body_ratio: float,
        shadow_ratio: float,
        deposit: float = 0.0,
        min_volume: float = 0.02,
        safe_factor: float = 0.02,
        engine_service_name: str = "",
        strategy_operator_service_name: str = "",
        min_price_delta: float = 1,
        background: Background = Background.FLAT_REV,
        power: Power = Power.WEAK,
        higher_edge: float = 70000,
        lower_edge: float = 69000,
    ) -> None:
        self.prelude_len = prelude_len
        self.window_len = window_len
        self.risk_per_full_trade_value = risk_per_full_trade
        self.partial_trade_multiplier_value = partial_trade_multiplier
        self.min_volume_value = min_volume
        self.safe_factor_value = safe_factor
        self.deposit_value = deposit
        self.engine_service_name_value = engine_service_name
        self.strategy_operator_service_name_value = strategy_operator_service_name
        self.background_value = background
        self.min_price_delta_value = min_price_delta
        self.body_ratio_value = body_ratio
        self.shadow_ratio_value = shadow_ratio
        self.power_value=power
        self.hightr_edge_value = higher_edge
        self.lower_edge_value = lower_edge

        self.order_value = Order()
        self.report_value = Report()
        self.spread_value: float = 0.0
        self.last_ptofit_value: float = 0.0
        self.entrypoint_value: Entrypoint
        self.trade_id_value: int = 0

    def set_payload(self, payload: Payload) -> None:
        self.payload_value = payload

    def set_order(self, order: Order) -> None:
        self.order_value = order

    def order(self) -> Order:
        return self.order_value

    def order_reset(self) -> None:
        self.order_value = Order()

    def set_report(self, report: Report) -> None:
        self.report_value = report

    def report(self) -> Report:
        return self.report_value

    def clear_report(self) -> None:
        self.report_value = Report()

    def pre_len(self) -> int:
        return self.prelude_len

    def window_maxlen(self) -> int:
        return self.window_len

    def deposit(self) -> float:
        return self.deposit_value

    def set_deposit(self, deposit: float) -> None:
        self.deposit_value = deposit

    def spread(self) -> float:
        return self.spread_value

    def set_spread(self, spread: float) -> None:
        self.spread_value = spread

    def risk_per_full_trade(self) -> float:
        return self.risk_per_full_trade_value

    def partial_trade_multiplier(self) -> float:
        return self.partial_trade_multiplier_value

    def min_volume(self) -> float:
        return self.min_volume_value

    def engine_service_name(self) -> str:
        return self.engine_service_name_value

    def strategy_operator_service_name(self) -> str:
        return self.strategy_operator_service_name_value

    def report_reset(self) -> None:
        self.report_value = Report()

    def background(self) -> Background:
        return self.background_value

    def set_background(self, background: Background) -> None:
        self.background_value = background

    def power(self) -> Power:
        return self.power_value

    def set_power(self, power: Power) -> None:
        self.power_value = power

    def safe_factor(self) -> float:
        return self.safe_factor_value

    def set_safe_factor(self, safe_factor: float) -> None:
        self.safe_factor_value = safe_factor

    def min_price_delta(self) -> float:
        return self.min_price_delta_value

    def body_ratio(self) -> float:
        return self.body_ratio_value

    def shadow_ratio(self) -> float:
        return self.shadow_ratio_value

    def entrypoint(self) -> Entrypoint:
        return self.entrypoint_value

    def set_entrypoint(self, entrypoint: Entrypoint) -> None:
        self.entrypoint_value = entrypoint

    def trade_id(self) -> int:
        return self.trade_id_value

    def set_trade_id(self, trade_id: int) -> None:
        self.trade_id_value = trade_id

    def higher_edge(self) -> float:
        return self.hightr_edge_value

    def lower_edge(self) -> float:
        return self.lower_edge_value
