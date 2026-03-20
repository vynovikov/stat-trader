from dataclasses import dataclass, field

from services.trade_engine.interface import TradeEngine


@dataclass
class Stat:
    def __init__(
        self,
        name: str,
        trade_engine: TradeEngine,
    ):
        self.name = name
        self.trade_engine = trade_engine
        self.profit: float = 0.0
        self.profit_trades: int = 0
        self.loss_trades: int = 0
        self.sl_trades: int = 0
        self.total_trades: int = 0
