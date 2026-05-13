import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

env_path = Path(__file__).parent.parent.parent / ".env.trade_engine"
load_dotenv(dotenv_path=env_path, override=True)


class Config(BaseModel):
    BACKGROUND: int = Field(...)
    POWER: int = Field(...)

    SYMBOL: str = Field(..., min_length=3)
    TIMEFRAME: str = Field(..., min_length=2)
    MIN_PRICE_DELTA: float = Field(...)
    RISK_PER_FULL_TRADE: float = Field(...)
    PARTIAL_TRADE_MULTIPLIER: float = Field(...)

    HIGHER_EDGE: float = Field(...)
    LOWER_EDGE: float = Field(...)
    MARGIN: float = Field(...)

    BODY_RATIO: float = Field(...)
    SHADOW_RATIO: float = Field(...)

    LOCAL_ADDR: str = Field(..., min_length=1)
    BACKEND_ADDR: str = Field(..., min_length=7)

    CLICKHOUSE_HOST: str = Field(..., min_length=3)
    CLICKHOUSE_PORT: int = Field(..., ge=1, le=65535)
    CLICKHOUSE_USER: str = Field(...)
    CLICKHOUSE_PASS: str = Field(...)
    CLICKHOUSE_DB: str = Field(...)

    ENGINE_LABEL_REV: str = Field(..., min_length=3)
    ENGINE_LABEL_CON: str = Field(..., min_length=3)
    ENGINE_LABEL_FLAT: str = Field(..., min_length=3)
    STRATEGY_OPERATOR_LABEL_REV: str = Field(..., min_length=3)
    STRATEGY_OPERATOR_LABEL_CON: str = Field(..., min_length=3)
    STRATEGY_OPERATOR_LABEL_FLAT: str = Field(..., min_length=3)

    BUY_TP: str = Field(...)
    SELL_TP: str = Field(...)
    BUY_LOSS: str = Field(...)
    SELL_LOSS: str = Field(...)
    BUY_SL: str = Field(...)
    SELL_SL: str = Field(...)
    BUY_CANCEL: str = Field(...)
    SELL_CANCEL: str = Field(...)

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            BACKGROUND=int(os.getenv("BACKGROUND", "")),
            POWER=int(os.getenv("POWER", "")),
            SYMBOL=os.getenv("SYMBOL", ""),
            TIMEFRAME=os.getenv("TIMEFRAME", ""),
            MIN_PRICE_DELTA=float(os.getenv("MIN_PRICE_DELTA", "")),
            RISK_PER_FULL_TRADE=float(os.getenv("RISK_PER_FULL_TRADE", "")),
            PARTIAL_TRADE_MULTIPLIER=float(os.getenv("PARTIAL_TRADE_MULTIPLIER", "")),
            HIGHER_EDGE=float(os.getenv("HIGHER_EDGE", "")),
            LOWER_EDGE=float(os.getenv("LOWER_EDGE", "")),
            MARGIN=float(os.getenv("MARGIN", "")),
            BODY_RATIO=float(os.getenv("BODY_RATIO", "")),
            SHADOW_RATIO=float(os.getenv("SHADOW_RATIO", "")),
            LOCAL_ADDR=os.getenv("LOCAL_ADDR", ""),
            BACKEND_ADDR=os.getenv("BACKEND_ADDR", ""),
            CLICKHOUSE_HOST=os.getenv("CLICKHOUSE_HOST", ""),
            CLICKHOUSE_PORT=int(os.getenv("CLICKHOUSE_PORT", "")),
            CLICKHOUSE_USER=os.getenv("CLICKHOUSE_USER", ""),
            CLICKHOUSE_PASS=os.getenv("CLICKHOUSE_PASS", ""),
            CLICKHOUSE_DB=os.getenv("CLICKHOUSE_DB", ""),
            ENGINE_LABEL_REV=os.getenv("ENGINE_LABEL_REV", ""),
            ENGINE_LABEL_CON=os.getenv("ENGINE_LABEL_CON", ""),
            ENGINE_LABEL_FLAT=os.getenv("ENGINE_LABEL_FLAT", ""),
            STRATEGY_OPERATOR_LABEL_REV=os.getenv("STRATEGY_OPERATOR_LABEL_REV", ""),
            STRATEGY_OPERATOR_LABEL_CON=os.getenv("STRATEGY_OPERATOR_LABEL_CON", ""),
            STRATEGY_OPERATOR_LABEL_FLAT=os.getenv("STRATEGY_OPERATOR_LABEL_FLAT", ""),
            BUY_TP=os.getenv("BUY_TP", ""),
            SELL_TP=os.getenv("SELL_TP", ""),
            BUY_LOSS=os.getenv("BUY_LOSS", ""),
            SELL_LOSS=os.getenv("SELL_LOSS", ""),
            BUY_SL=os.getenv("BUY_SL", ""),
            SELL_SL=os.getenv("SELL_SL", ""),
            BUY_CANCEL=os.getenv("BUY_CANCEL", ""),
            SELL_CANCEL=os.getenv("SELL_CANCEL", ""),
        )


if __name__ == "__main__":
    cfg = Config.from_env()
    print(cfg)
