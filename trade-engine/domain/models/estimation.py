from typing import NamedTuple

from domain.types.category import Category


class Estimation(NamedTuple):
    category: Category
    profit: float = 0.0
    risk: float = 0.0
    profit_risk_ratio: float = 0.0
