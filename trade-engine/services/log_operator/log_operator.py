from services.log_operator.interface import LogOperator

class LogOperatorImpl(LogOperator):
    def log_level(
        self,
        event: str,
    ) -> str:
        if event in [
            "triggered_uptrend",
            "triggered_downtrend",
            "orders_canceled",
            "entry_triggered",
            "TP_triggered",
            "SL_triggered",
            ]:

                return "warning"

        return "info"

    def log_string(
        self,
        cooldown: int,
        initial_state: str,
        event: str,
        final_state: str,
        ) -> str:
        result=""
        log_prefix=""

        match True:
            case _ if event in [
            "triggered_uptrend",
            "triggered_downtrend",
            "orders_canceled",
            ]:
                log_prefix="ORDERS"

            case _ if event in [
                "entry_triggered",
                "TP_triggered",
                "SL_triggered",
            ]:
                log_prefix="TRIGGER"

        if len(log_prefix)>0:
            result+=f"{log_prefix}, "

        result+=(
            f"cooldown = {cooldown}: "
            f"{initial_state} -> ({event}) -> {final_state}"
        )

        return result
