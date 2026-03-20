from typing import Tuple
from domain.models.order import Order
from domain.models.decision import Decision
from domain.models.report import Report
from domain.types.market_action import MarketAction


class PriorityOperator:
    def prioritize(
        self,
        decision_primary: Decision,
        decision_secondary: Decision,
    ) -> Tuple[str, MarketAction, Order, Report]:
        final_engine_id: str
        final_market_action: MarketAction
        final_order: Order
        final_report: Report

        match decision_primary.action:
            case MarketAction.HOLD:
                final_order = Order()

                match decision_secondary.action:
                    case MarketAction.HOLD:
                        final_engine_id = ""
                        final_market_action = MarketAction.HOLD
                        final_order = Order()
                        final_report = Report()
                    case MarketAction.OPEN:
                        final_engine_id = decision_secondary.engine_id
                        final_market_action = MarketAction.OPEN
                        final_order = decision_secondary.order
                        final_report = Report()
                    case MarketAction.CLOSE:
                        final_engine_id = decision_secondary.engine_id
                        final_market_action = MarketAction.CLOSE
                        final_order = Order()
                        final_report = decision_secondary.report

            case MarketAction.OPEN:
                final_order = decision_primary.order

                match decision_secondary.action:
                    case MarketAction.HOLD:
                        final_engine_id = decision_primary.engine_id
                        final_market_action = MarketAction.OPEN
                        final_report = Report()
                    case MarketAction.OPEN:
                        final_engine_id = decision_primary.engine_id
                        final_market_action = MarketAction.OPEN
                        final_report = Report()
                    case MarketAction.CLOSE:
                        final_engine_id = decision_primary.engine_id
                        final_market_action = MarketAction.CLOSE_THEN_OPEN
                        final_report = decision_secondary.report

            case MarketAction.CLOSE:
                match decision_secondary.action:
                    case MarketAction.HOLD:
                        final_engine_id = decision_primary.engine_id
                        final_market_action = MarketAction.CLOSE
                        final_order = Order()
                        final_report = decision_primary.report
                    case MarketAction.OPEN:
                        final_engine_id = decision_primary.engine_id
                        final_market_action = MarketAction.CLOSE_THEN_OPEN
                        final_order = decision_secondary.order
                        final_report = decision_primary.report
                    case MarketAction.CLOSE:
                        final_engine_id = decision_primary.engine_id
                        final_market_action = MarketAction.CLOSE
                        final_order = Order()
                        final_report = decision_primary.report

        return final_engine_id, final_market_action, final_order, final_report
