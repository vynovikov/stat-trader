from dataclasses import dataclass

from domain.types.category import Category
from domain.types.direction import Direction


@dataclass
class Payload:
    category: Category = Category.NONE
    profit: float = 0.0
    risk: float = 0.0
    profit_risk_ratio: float = 0.0

    sl_triggered: bool = False

    direction: Direction = Direction.UNKNOWN

    def to_dict(self) -> dict:
        """Convert the Payload to a dictionary."""
        return {
            "category": (
                self.category.value
                if isinstance(self.category, Category)
                else self.category
            ),
            "profit": self.profit,
            "risk": self.risk,
            "profit_risk_ratio": self.profit_risk_ratio,
        }
