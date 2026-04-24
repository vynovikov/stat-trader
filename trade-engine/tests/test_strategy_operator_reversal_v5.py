import pytest
import logging

from typing import Any, Dict, List
from logging import LoggerAdapter

from domain.types.candle import Candle
from domain.types.background import Background
from domain.types.entrypoint import Entrypoint

from services.bookkeeper.leveraged_bookkeeper import LeveragedBookkeeper
from services.strategy_operator.strategy_operator_reversal_v5_trend import (
    StrategyOperatorReversalV5,
)

def trade_engine_logger(label: str) -> LoggerAdapter:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)

    formatter = logging.Formatter("    - %(levelname)s: [%(engine_id)s] %(message)s")
    stream_handler.setFormatter(formatter)

    base_logger = logging.getLogger(label)
    base_logger.setLevel(logging.INFO)
    base_logger.addHandler(stream_handler)

    logger = logging.LoggerAdapter(base_logger, {"engine_id": label})

    return logger

entrypoint_test_cases: List[Dict[str, Any]] = [
    {
        "name": "0. Candles UP DOWN DOWN DOWN DOWN. Background = Background.FLAT_REV",
        "candles": [
            Candle(open=100, close=100.1, high=100.5, low=99.5),
            Candle(open=100.1, close=100, high=101.5, low=99.5),
            Candle(open=100, close=99.9, high=100.05, low=99.95),
            Candle(open=99.9, close=99.8, high=100.95, low=99.75),
            Candle(open=99.8, close=99.7, high=99.85, low=99.65),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.FLAT_REV,
        "expected_entrypoint": Entrypoint.BUY,
    },
    {
        "name": "1. Candles UP DOWN DOWN DOWN DOWN. Background = Background.BULLISH_REV",
        "candles": [
            Candle(open=100, close=100.1, high=100.5, low=99.5),
            Candle(open=100.1, close=100, high=101.5, low=99.5),
            Candle(open=100, close=99.9, high=100.05, low=99.95),
            Candle(open=99.9, close=99.8, high=100.95, low=99.75),
            Candle(open=99.8, close=99.7, high=99.85, low=99.65),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BULLISH_REV,
        "expected_entrypoint": Entrypoint.BUY,
    },
    {
        "name": "2. Candles UP DOWN DOWN DOWN DOWN. Background = Background.BEARISH_REV",
        "candles": [
            Candle(open=100, close=100.1, high=100.5, low=99.5),
            Candle(open=100.1, close=100, high=101.5, low=99.5),
            Candle(open=100, close=99.9, high=100.05, low=99.95),
            Candle(open=99.9, close=99.8, high=100.95, low=99.75),
            Candle(open=99.8, close=99.7, high=99.85, low=99.65),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BEARISH_REV,
        "expected_entrypoint": Entrypoint.UNKNOWN,
    },
    {
        "name": "3. Candles UP DOWN DOWN DOWN DOWN. Background = Background.BULLISH_CON",
        "candles": [
            Candle(open=100, close=100.1, high=100.5, low=99.5),
            Candle(open=100.1, close=100, high=101.5, low=99.5),
            Candle(open=100, close=99.9, high=100.05, low=99.95),
            Candle(open=99.9, close=99.8, high=100.95, low=99.75),
            Candle(open=99.8, close=99.7, high=99.85, low=99.65),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BULLISH_CON,
        "expected_entrypoint": Entrypoint.UNKNOWN,
    },
    {
        "name": "4. Candles UP DOWN DOWN DOWN DOWN. Background = Background.BULLISH_CON_REV",
        "candles": [
            Candle(open=100, close=100.1, high=100.5, low=99.5),
            Candle(open=100.1, close=100, high=101.5, low=99.5),
            Candle(open=100, close=99.9, high=100.05, low=99.95),
            Candle(open=99.9, close=99.8, high=100.95, low=99.75),
            Candle(open=99.8, close=99.7, high=99.85, low=99.65),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BULLISH_CON_REV,
        "expected_entrypoint": Entrypoint.BUY,
    },
    {
        "name": "5. Candles DOWN UP DOWN DOWN DOWN. Engulfs = True. Background = Background.FLAT_REV",
        "candles": [
            Candle(open=100, close=99.9, high=100.5, low=99.85),
            Candle(open=99.9, close=99.93, high=99.97, low=99.85),
            Candle(open=99.93, close=99.83, high=99.98, low=99.8),
            Candle(open=99.83, close=99.73, high=100.95, low=99.7),
            Candle(open=99.73, close=99.63, high=99.85, low=99.6),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.FLAT_REV,
        "expected_entrypoint": Entrypoint.BUY,
    },
    {
        "name": "6. Candles DOWN UP DOWN DOWN DOWN. Engulfs = True. Background = Background.BULLISH_REV",
        "candles": [
            Candle(open=100, close=99.9, high=100.5, low=99.85),
            Candle(open=99.9, close=99.93, high=99.97, low=99.85),
            Candle(open=99.93, close=99.83, high=99.98, low=99.8),
            Candle(open=99.83, close=99.73, high=100.95, low=99.7),
            Candle(open=99.73, close=99.63, high=99.85, low=99.6),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BULLISH_REV,
        "expected_entrypoint": Entrypoint.BUY,
    },
    {
        "name": "7. Candles DOWN UP DOWN DOWN DOWN. Engulfs = True. Background = Background.BULLISH_CON_REV",
        "candles": [
            Candle(open=100, close=99.9, high=100.5, low=99.85),
            Candle(open=99.9, close=99.93, high=99.97, low=99.85),
            Candle(open=99.93, close=99.83, high=99.98, low=99.8),
            Candle(open=99.83, close=99.73, high=100.95, low=99.7),
            Candle(open=99.73, close=99.63, high=99.85, low=99.6),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BULLISH_CON_REV,
        "expected_entrypoint": Entrypoint.BUY,
    },
    {
        "name": "8. Candles DOWN UP DOWN DOWN DOWN. Engulfs = True. Background = Background.BULLISH_CON",
        "candles": [
            Candle(open=100, close=99.9, high=100.5, low=99.85),
            Candle(open=99.9, close=99.93, high=99.97, low=99.85),
            Candle(open=99.93, close=99.83, high=99.98, low=99.8),
            Candle(open=99.83, close=99.73, high=100.95, low=99.7),
            Candle(open=99.73, close=99.63, high=99.85, low=99.6),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BULLISH_CON,
        "expected_entrypoint": Entrypoint.UNKNOWN,
    },
    {
        "name": "9. Candles DOWN UP DOWN DOWN DOWN. Engulfs = True. Background = Background.BEARISH_REV",
        "candles": [
            Candle(open=100, close=99.9, high=100.5, low=99.85),
            Candle(open=99.9, close=99.93, high=99.97, low=99.85),
            Candle(open=99.93, close=99.83, high=99.98, low=99.8),
            Candle(open=99.83, close=99.73, high=100.95, low=99.7),
            Candle(open=99.73, close=99.63, high=99.85, low=99.6),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BEARISH_REV,
        "expected_entrypoint": Entrypoint.UNKNOWN,
    },
    {
        "name": "10. Candles DOWN UP DOWN DOWN DOWN.Engulfs = False. Background = Background.BEARISH_REV",
        "candles": [
            Candle(open=100, close=99.9, high=100.5, low=99.85),
            Candle(open=99.9, close=99.95, high=99.97, low=99.85),
            Candle(open=99.95, close=99.85, high=99.98, low=99.8),
            Candle(open=99.85, close=99.75, high=100.95, low=99.7),
            Candle(open=99.75, close=99.65, high=99.85, low=99.6),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.FLAT_REV,
        "expected_entrypoint": Entrypoint.UNKNOWN,
    },
    {
        "name": "11. Candles DOWN DOWN UP DOWN DOWN. Engulfs = True. Background = Background.FLAT_REV",
        "candles": [
            Candle(open=100, close=99.9, high=100.5, low=99.85),
            Candle(open=99.9, close=99.8, high=99.95, low=99.85),
            Candle(open=99.8, close=99.83, high=99.88, low=99.78),
            Candle(open=99.83, close=99.73, high=100.9, low=99.7),
            Candle(open=99.73, close=99.63, high=99.8, low=99.6),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.FLAT_REV,
        "expected_entrypoint": Entrypoint.BUY,
    },
    {
        "name": "12. Candles DOWN DOWN UP DOWN DOWN. Engulfs = True. Background = Background.BULLISH_REV",
        "candles": [
            Candle(open=100, close=99.9, high=100.5, low=99.85),
            Candle(open=99.9, close=99.8, high=99.95, low=99.85),
            Candle(open=99.8, close=99.83, high=99.88, low=99.78),
            Candle(open=99.83, close=99.73, high=100.9, low=99.7),
            Candle(open=99.73, close=99.63, high=99.8, low=99.6),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BULLISH_REV,
        "expected_entrypoint": Entrypoint.BUY,
    },
    {
        "name": "13. Candles DOWN DOWN UP DOWN DOWN. Background = Background.BEARISH_REV",
        "candles": [
            Candle(open=100, close=99.9, high=100.5, low=99.85),
            Candle(open=99.9, close=99.8, high=99.95, low=99.85),
            Candle(open=99.8, close=99.83, high=99.88, low=99.78),
            Candle(open=99.83, close=99.73, high=100.9, low=99.7),
            Candle(open=99.73, close=99.63, high=99.8, low=99.6),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BEARISH_REV,
        "expected_entrypoint": Entrypoint.UNKNOWN,
    },
    {
        "name": "14. Candles DOWN DOWN UP DOWN DOWN. Background = Background.BEARISH_REV",
        "candles": [
            Candle(open=100, close=99.9, high=100.5, low=99.85),
            Candle(open=99.9, close=99.8, high=99.95, low=99.85),
            Candle(open=99.8, close=99.83, high=99.88, low=99.78),
            Candle(open=99.83, close=99.73, high=100.9, low=99.7),
            Candle(open=99.73, close=99.63, high=99.8, low=99.6),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BULLISH_CON,
        "expected_entrypoint": Entrypoint.UNKNOWN,
    },
    {
        "name": "15. Candles DOWN DOWN UP DOWN DOWN. Engulfs = False. Background = Background.BEARISH_REV",
        "candles": [
            Candle(open=100, close=99.9, high=100.5, low=99.85),
            Candle(open=99.9, close=99.8, high=99.95, low=99.85),
            Candle(open=99.8, close=99.85, high=99.88, low=99.78),
            Candle(open=99.85, close=99.75, high=100.9, low=99.7),
            Candle(open=99.75, close=99.65, high=99.8, low=99.6),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.FLAT_REV,
        "expected_entrypoint": Entrypoint.UNKNOWN,
    },
    {
        "name": "16. Candles DOWN DOWN DOWN UP DOWN. Engulfs = True. Background = Background.FLAT_REV",
        "candles": [
            Candle(open=100, close=99.9, high=100.5, low=99.85),
            Candle(open=99.9, close=99.8, high=99.95, low=99.75),
            Candle(open=99.8, close=99.7, high=99.85, low=99.65),
            Candle(open=99.7, close=99.73, high=99.78, low=99.69),
            Candle(open=99.83, close=99.73, high=99.69, low=99.59),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.FLAT_REV,
        "expected_entrypoint": Entrypoint.BUY,
    },
    {
        "name": "17. Candles DOWN DOWN DOWN UP DOWN. Engulfs = True. Background = Background.BULLISH_REV",
        "candles": [
            Candle(open=100, close=99.9, high=100.5, low=99.85),
            Candle(open=99.9, close=99.8, high=99.95, low=99.75),
            Candle(open=99.8, close=99.7, high=99.85, low=99.65),
            Candle(open=99.7, close=99.73, high=99.78, low=99.69),
            Candle(open=99.83, close=99.73, high=99.69, low=99.59),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BULLISH_REV,
        "expected_entrypoint": Entrypoint.BUY,
    },
    {
        "name": "18. Candles DOWN DOWN DOWN UP DOWN. Background = Background.BEARISH_REV",
        "candles": [
            Candle(open=100, close=99.9, high=100.5, low=99.85),
            Candle(open=99.9, close=99.8, high=99.95, low=99.75),
            Candle(open=99.8, close=99.7, high=99.85, low=99.65),
            Candle(open=99.7, close=99.73, high=99.78, low=99.69),
            Candle(open=99.83, close=99.73, high=99.69, low=99.59),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BEARISH_REV,
        "expected_entrypoint": Entrypoint.UNKNOWN,
    },
    {
        "name": "19. Candles DOWN DOWN DOWN UP DOWN. Background = Background.BULLISH_CON",
        "candles": [
            Candle(open=100, close=99.9, high=100.5, low=99.85),
            Candle(open=99.9, close=99.8, high=99.95, low=99.75),
            Candle(open=99.8, close=99.7, high=99.85, low=99.65),
            Candle(open=99.7, close=99.73, high=99.78, low=99.69),
            Candle(open=99.83, close=99.73, high=99.69, low=99.59),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BULLISH_CON,
        "expected_entrypoint": Entrypoint.UNKNOWN,
    },
    {
        "name": "20. Candles DOWN DOWN DOWN UP DOWN. Engulfs = False. Background = Background.FLAT_REV",
        "candles": [
            Candle(open=100, close=99.9, high=100.5, low=99.85),
            Candle(open=99.9, close=99.8, high=99.95, low=99.75),
            Candle(open=99.8, close=99.7, high=99.85, low=99.65),
            Candle(open=99.7, close=99.75, high=99.78, low=99.69),
            Candle(open=99.85, close=99.75, high=99.9, low=99.65),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.FLAT_REV,
        "expected_entrypoint": Entrypoint.UNKNOWN,
    },
    {
        "name": "21. Candles DOWN DOWN DOWN DOWN DOWN. Background = Background.BULLISH_REV",
        "candles": [
            Candle(open=100.1, close=100, high=100.15, low=99.95),
            Candle(open=100, close=99.9, high=100.05, low=99.85),
            Candle(open=99.9, close=99.8, high=99.95, low=99.75),
            Candle(open=99.8, close=99.7, high=99.85, low=99.65),
            Candle(open=99.7, close=99.6, high=99.75, low=99.55),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BULLISH_REV,
        "expected_entrypoint": Entrypoint.BUY,
    },
    {
        "name": "22. Candles DOWN DOWN DOWN DOWN DOWN. Background = Background.BEARISH_REV",
        "candles": [
            Candle(open=100.1, close=100, high=100.15, low=99.95),
            Candle(open=100, close=99.9, high=100.05, low=99.85),
            Candle(open=99.9, close=99.8, high=99.95, low=99.75),
            Candle(open=99.8, close=99.7, high=99.85, low=99.65),
            Candle(open=99.7, close=99.6, high=99.75, low=99.55),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BEARISH_REV,
        "expected_entrypoint": Entrypoint.UNKNOWN,
    },
    {
        "name": "23. Candles DOWN DOWN DOWN DOWN DOWN. Background = Background.BULLISH_CON",
        "candles": [
            Candle(open=100.1, close=100, high=100.15, low=99.95),
            Candle(open=100, close=99.9, high=100.05, low=99.85),
            Candle(open=99.9, close=99.8, high=99.95, low=99.75),
            Candle(open=99.8, close=99.7, high=99.85, low=99.65),
            Candle(open=99.7, close=99.6, high=99.75, low=99.55),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BULLISH_CON,
        "expected_entrypoint": Entrypoint.UNKNOWN,
    },
    {
        "name": "24. Candles DOWN DOWN DOWN DOWN DOWN. Background = Background.BULLISH_CON_REV",
        "candles": [
            Candle(open=100.1, close=100, high=100.15, low=99.95),
            Candle(open=100, close=99.9, high=100.05, low=99.85),
            Candle(open=99.9, close=99.8, high=99.95, low=99.75),
            Candle(open=99.8, close=99.7, high=99.85, low=99.65),
            Candle(open=99.7, close=99.6, high=99.75, low=99.55),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BULLISH_CON_REV,
        "expected_entrypoint": Entrypoint.BUY,
    },
    {
        "name": "25. Candles DOWN UP UP UP UP.  Background = Background.FLAT_REV",
        "candles": [
            Candle(open=100.1, close=100, high=100.15, low=99.95),
            Candle(open=100, close=100.1, high=101.5, low=99.5),
            Candle(open=100.1, close=100.2, high=100.15, low=100.05),
            Candle(open=100.2, close=100.3, high=100.25, low=100.15),
            Candle(open=100.3, close=100.4, high=99.35, low=100.25),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.FLAT_REV,
        "expected_entrypoint": Entrypoint.SELL,
    },
    {
        "name": "26. Candles DOWN UP UP UP UP.  Background = Background.BULLISH_REV",
        "candles": [
            Candle(open=100.1, close=100, high=100.15, low=99.95),
            Candle(open=100, close=100.1, high=101.5, low=99.5),
            Candle(open=100.1, close=100.2, high=100.15, low=100.05),
            Candle(open=100.2, close=100.3, high=100.25, low=100.15),
            Candle(open=100.3, close=100.4, high=99.35, low=100.25),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BULLISH_REV,
        "expected_entrypoint": Entrypoint.UNKNOWN,
    },
    {
        "name": "27. Candles DOWN UP UP UP UP.  Background = Background.BULLISH_REV",
        "candles": [
            Candle(open=100.1, close=100, high=100.15, low=99.95),
            Candle(open=100, close=100.1, high=101.5, low=99.5),
            Candle(open=100.1, close=100.2, high=100.15, low=100.05),
            Candle(open=100.2, close=100.3, high=100.25, low=100.15),
            Candle(open=100.3, close=100.4, high=99.35, low=100.25),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BEARISH_CON,
        "expected_entrypoint": Entrypoint.UNKNOWN,
    },
    {
        "name": "28. Candles DOWN UP UP UP UP. Background = Background.BEARISH_REV",
        "candles": [
            Candle(open=100.1, close=100, high=100.15, low=99.95),
            Candle(open=100, close=100.1, high=101.5, low=99.5),
            Candle(open=100.1, close=100.2, high=100.15, low=100.05),
            Candle(open=100.2, close=100.3, high=100.25, low=100.15),
            Candle(open=100.3, close=100.4, high=99.35, low=100.25),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BEARISH_REV,
        "expected_entrypoint": Entrypoint.SELL,
    },
    {
        "name": "29. Candles UP DOWN UP UP UP. Engulfs = True. Background = Background.BULLISH_REV",
        "candles": [
            Candle(open=100, close=100.1, high=100.15, low=99.95),
            Candle(open=100.1, close=100.07, high=100.15, low=100.2),
            Candle(open=100.07, close=100.17, high=100.2, low=100),
            Candle(open=100.17, close=100.27, high=100.3, low=100.15),
            Candle(open=100.27, close=100.37, high=100.4, low=100.25),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BULLISH_REV,
        "expected_entrypoint": Entrypoint.UNKNOWN,
    },
    {
        "name": "30. Candles UP DOWN UP UP UP. Engulfs = True. Background = Background.BEARISH_CON",
        "candles": [
            Candle(open=100, close=100.1, high=100.15, low=99.95),
            Candle(open=100.1, close=100.07, high=100.15, low=100.2),
            Candle(open=100.07, close=100.17, high=100.2, low=100),
            Candle(open=100.17, close=100.27, high=100.3, low=100.15),
            Candle(open=100.27, close=100.37, high=100.4, low=100.25),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BEARISH_CON,
        "expected_entrypoint": Entrypoint.UNKNOWN,
    },
    {
        "name": "31. Candles UP DOWN UP UP UP. Engulfs = True. Background = Background.BEARISH_REV",
        "candles": [
            Candle(open=100, close=100.1, high=100.15, low=99.95),
            Candle(open=100.1, close=100.07, high=100.15, low=100.05),
            Candle(open=100.07, close=100.17, high=100.2, low=100),
            Candle(open=100.17, close=100.27, high=100.3, low=100.15),
            Candle(open=100.27, close=100.37, high=100.4, low=100.25),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BEARISH_REV,
        "expected_entrypoint": Entrypoint.SELL,
    },
    {
        "name": "32. Candles UP DOWN UP UP UP. Engulfs = False. Background = Background.FLAT_REV, Entrypoint = Entrypoint.UNKNOWN",
        "candles": [
            Candle(open=100, close=100.1, high=100.15, low=99.95),
            Candle(open=100.1, close=100.05, high=100.15, low=100.05),
            Candle(open=100.05, close=100.15, high=100.2, low=100),
            Candle(open=100.15, close=100.25, high=100.3, low=100.15),
            Candle(open=100.25, close=100.35, high=100.4, low=100.25),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.FLAT_REV,
        "expected_entrypoint": Entrypoint.UNKNOWN,
    },
    {
        "name": "33. Candles UP UP DOWN UP UP. Engulfs = True. Background = Background.FLAT_REV",
        "candles": [
            Candle(open=100, close=100.1, high=100.15, low=99.95),
            Candle(open=100.1, close=100.2, high=100.25, low=100.15),
            Candle(open=100.2, close=100.17, high=100.24, low=100.15),
            Candle(open=100.17, close=100.27, high=100.3, low=100.15),
            Candle(open=100.27, close=100.37, high=100.4, low=100.25),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.FLAT_REV,
        "expected_entrypoint": Entrypoint.SELL,
    },
    {
        "name": "34. Candles UP UP DOWN UP UP. Engulfs = True. Background = Background.BULLISH_REV",
        "candles": [
            Candle(open=100, close=100.1, high=100.15, low=99.95),
            Candle(open=100.1, close=100.2, high=100.25, low=100.15),
            Candle(open=100.2, close=100.17, high=100.24, low=100.15),
            Candle(open=100.17, close=100.27, high=100.3, low=100.15),
            Candle(open=100.27, close=100.37, high=100.4, low=100.25),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BULLISH_REV,
        "expected_entrypoint": Entrypoint.UNKNOWN,
    },
    {
        "name": "35. Candles UP UP DOWN UP UP. Engulfs = True. Background = Background.BEARISH_CON",
        "candles": [
            Candle(open=100, close=100.1, high=100.15, low=99.95),
            Candle(open=100.1, close=100.2, high=100.25, low=100.15),
            Candle(open=100.2, close=100.17, high=100.24, low=100.15),
            Candle(open=100.17, close=100.27, high=100.3, low=100.15),
            Candle(open=100.27, close=100.37, high=100.4, low=100.25),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BEARISH_CON,
        "expected_entrypoint": Entrypoint.UNKNOWN,
    },
    {
        "name": "36. Candles UP UP DOWN UP UP. Background = Background.BEARISH_REV",
        "candles": [
            Candle(open=100, close=100.1, high=100.15, low=99.95),
            Candle(open=100.1, close=100.2, high=100.25, low=100.15),
            Candle(open=100.2, close=100.17, high=100.24, low=100.15),
            Candle(open=100.17, close=100.27, high=100.3, low=100.15),
            Candle(open=100.27, close=100.37, high=100.4, low=100.25),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BEARISH_REV,
        "expected_entrypoint": Entrypoint.SELL,
    },
    {
        "name": "37. Candles UP UP DOWN UP UP. Engulfs = False. Background = Background.BEARISH_REV",
        "candles": [
            Candle(open=100, close=100.1, high=100.15, low=99.95),
            Candle(open=100.1, close=100.2, high=100.25, low=100.15),
            Candle(open=100.2, close=100.16, high=100.24, low=100.15),
            Candle(open=100.16, close=100.26, high=100.3, low=100.15),
            Candle(open=100.26, close=100.36, high=100.4, low=100.25),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.FLAT_REV,
        "expected_entrypoint": Entrypoint.UNKNOWN,
    },
    {
        "name": "38. Candles UP UP UP DOWN UP. Engulfs = True. Background = Background.FLAT_REV",
        "candles": [
            Candle(open=100, close=100.1, high=100.15, low=99.95),
            Candle(open=100.1, close=100.2, high=100.25, low=100.05),
            Candle(open=100.2, close=100.3, high=100.35, low=100.15),
            Candle(open=100.3, close=100.27, high=100.33, low=100.22),
            Candle(open=100.27, close=100.37, high=100.4, low=100.2),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.FLAT_REV,
        "expected_entrypoint": Entrypoint.SELL,
    },
    {
        "name": "39. Candles UP UP UP DOWN UP. Engulfs = True. Background = Background.BULLISH_REV",
        "candles": [
            Candle(open=100, close=100.1, high=100.15, low=99.95),
            Candle(open=100.1, close=100.2, high=100.25, low=100.05),
            Candle(open=100.2, close=100.3, high=100.35, low=100.15),
            Candle(open=100.3, close=100.27, high=100.33, low=100.22),
            Candle(open=100.27, close=100.37, high=100.4, low=100.2),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BULLISH_REV,
        "expected_entrypoint": Entrypoint.UNKNOWN,
    },
    {
        "name": "40. Candles UP UP UP DOWN UP. Engulfs = True. Background = Background.BULLISH_REV",
        "candles": [
            Candle(open=100, close=100.1, high=100.15, low=99.95),
            Candle(open=100.1, close=100.2, high=100.25, low=100.05),
            Candle(open=100.2, close=100.3, high=100.35, low=100.15),
            Candle(open=100.3, close=100.27, high=100.33, low=100.22),
            Candle(open=100.27, close=100.37, high=100.4, low=100.2),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BEARISH_CON,
        "expected_entrypoint": Entrypoint.UNKNOWN,
    },
    {
        "name": "41. Candles UP UP UP DOWN UP. Background = Background.BEARISH_REV",
        "candles": [
            Candle(open=100, close=100.1, high=100.15, low=99.95),
            Candle(open=100.1, close=100.2, high=100.25, low=100.05),
            Candle(open=100.2, close=100.3, high=100.35, low=100.15),
            Candle(open=100.3, close=100.27, high=100.33, low=100.22),
            Candle(open=100.27, close=100.37, high=100.4, low=100.2),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BEARISH_REV,
        "expected_entrypoint": Entrypoint.SELL,
    },
    {
        "name": "42. Candles UP UP UP DOWN UP. Engulfs = False. Background = Background.BEARISH_REV",
        "candles": [
            Candle(open=100, close=100.1, high=100.15, low=99.95),
            Candle(open=100.1, close=100.2, high=100.25, low=100.05),
            Candle(open=100.2, close=100.3, high=100.35, low=100.15),
            Candle(open=100.3, close=100.25, high=100.33, low=100.22),
            Candle(open=100.25, close=100.35, high=100.4, low=100.2),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.FLAT_REV,
        "expected_entrypoint": Entrypoint.UNKNOWN,
    },
    {
        "name": "43. Candles UP UP UP UP UP.  Background = Background.FLAT_REV",
        "candles": [
            Candle(open=99.9, close=100, high=100.05, low=99.85),
            Candle(open=100, close=100.1, high=100.15, low=99.95),
            Candle(open=100.1, close=100.2, high=100.15, low=100.05),
            Candle(open=100.2, close=100.3, high=100.25, low=100.15),
            Candle(open=100.3, close=100.4, high=99.35, low=100.25),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.FLAT_REV,
        "expected_entrypoint": Entrypoint.SELL,
    },
    {
        "name": "44. Candles UP UP UP UP UP.  Background = Background.BULLISH_REV",
        "candles": [
            Candle(open=99.9, close=100, high=100.05, low=99.85),
            Candle(open=100, close=100.1, high=100.15, low=99.95),
            Candle(open=100.1, close=100.2, high=100.15, low=100.05),
            Candle(open=100.2, close=100.3, high=100.25, low=100.15),
            Candle(open=100.3, close=100.4, high=99.35, low=100.25),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BULLISH_REV,
        "expected_entrypoint": Entrypoint.UNKNOWN,
    },
    {
        "name": "45. Candles UP UP UP UP UP.  Background = Background.BULLISH_REV",
        "candles": [
            Candle(open=99.9, close=100, high=100.05, low=99.85),
            Candle(open=100, close=100.1, high=100.15, low=99.95),
            Candle(open=100.1, close=100.2, high=100.15, low=100.05),
            Candle(open=100.2, close=100.3, high=100.25, low=100.15),
            Candle(open=100.3, close=100.4, high=99.35, low=100.25),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BEARISH_CON,
        "expected_entrypoint": Entrypoint.UNKNOWN,
    },
    {
        "name": "46. Candles UP UP UP UP UP. Background = Background.BEARISH_REV",
        "candles": [
            Candle(open=99.9, close=100, high=100.05, low=99.85),
            Candle(open=100, close=100.1, high=100.15, low=99.95),
            Candle(open=100.1, close=100.2, high=100.15, low=100.05),
            Candle(open=100.2, close=100.3, high=100.25, low=100.15),
            Candle(open=100.3, close=100.4, high=99.35, low=100.25),
        ],
        "body_ratio": 0.4,
        "shadow_ratio": 1,
        "background": Background.BEARISH_REV,
        "expected_entrypoint": Entrypoint.SELL,
    },
]


@pytest.mark.parametrize(
    "case", entrypoint_test_cases, ids=[c["name"] for c in entrypoint_test_cases]
)
def test_strategy_operator_entrypoint(case):
    logger = trade_engine_logger("strategy_con_v6")
    leveraged_bookkeeper = LeveragedBookkeeper(leverage=10)
    strategy_operator = StrategyOperatorReversalV5(
        bookkeeper=leveraged_bookkeeper,
        logger=logger,
        )

    entrypoint = strategy_operator.entrypoint(
        candles=case["candles"],
        body_ratio=case["body_ratio"],
        shadow_ratio=case["shadow_ratio"],
        background=case["background"],
    )

    assert (
        entrypoint == case["expected_entrypoint"]
    ), f"expected_entrypoint {case["expected_entrypoint"]} but got {entrypoint}"
