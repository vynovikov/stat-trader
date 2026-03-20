from services.counter_operator.interface import CounterOperator


class CounterOperatorImpl(CounterOperator):
    def __init__(
        self,
        cooldown_counter_max: int = 0,
        last_id: int = 0,
        neighbor_limit: int = 4,
    ) -> None:
        self.cooldown_counter_max = cooldown_counter_max
        self.cooldown_counter_value = 0
        self.last_id_counter = last_id
        self.neighbor_limit_counter = neighbor_limit

    def last_id(self) -> int:
        return self.last_id_counter

    def last_id_inc(self) -> None:
        self.last_id_counter += 1

    def last_id_dec(self) -> None:
        if self.last_id_counter > 0:
            self.last_id_counter += 1

    def neighbor_limit(self) -> int:
        return self.neighbor_limit_counter

    def cooldown_counter(self) -> int:
        return self.cooldown_counter_value

    def cooldown_set(self) -> None:
        self.cooldown_counter_value = self.cooldown_counter_max

    def cooldown_dec(self) -> bool:
        self.cooldown_counter_value -= 1

        if self.cooldown_counter_value <= 0:

            return True

        return False
