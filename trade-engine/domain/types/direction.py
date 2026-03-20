from enum import Enum


class Direction(Enum):
    UP = "up"
    DOWN = "down"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            s = value.strip()
            for m in cls:
                if m.value == s.lower():
                    return m
            return cls.__members__.get(s.upper(), None)
        return None
