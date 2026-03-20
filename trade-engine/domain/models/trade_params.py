from dataclasses import dataclass
from datetime import datetime

from domain.types.category import Category
from domain.types.direction import Direction


@dataclass
class TradeParams:
    direction: Direction = Direction.UNKNOWN
    category: Category = Category.NONE
    profit: float = 0.0
    candles_num: int = 0
    created_at: datetime = datetime.min
    expire_at: datetime = datetime.min
    risk: float = 0.0
    profit_risk_ratio: float = 0.0
