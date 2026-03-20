from abc import ABC, abstractmethod


class LogOperator(ABC):
    @abstractmethod
    def log_level(
        self,
        event: str,
    ) -> str: ...

    @abstractmethod
    def log_string(
        self,
        cooldown: int,
        initial_state: str,
        event: str,
        final_state: str,
        ) -> str: ...