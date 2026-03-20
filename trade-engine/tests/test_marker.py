import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
import pandas as pd
import pytest

from domain.models.segment import Segment
from domain.models.trade_params import TradeParams
from domain.types.candle import Candle
from domain.types.category import Category
from domain.types.direction import Direction
from marker.marker import Marker
from services.estimator.reversal_estimator import ReversalEstimator

test_cases = [
    {
        "name": "0. Not enough data",
        "df": pd.DataFrame(
            {
                "Open": [95, 95],
                "High": [100, 100],
                "Low": [90, 90],
                "Close": [96, 95],
                "Volume": [1000, 1001],
            }
        ),
        "expected": [],
    },
    {
        "name": "1. No trend",
        "df": pd.DataFrame(
            {
                "Open": [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
                "High": [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
                "Low": [99, 100, 101, 102, 103, 104, 105, 106, 107, 108],
                "Close": [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
                "Volume": [1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009],
            }
        ),
        "expected": [],
    },
    {
        "name": "2. Uptrend with second candle stopping trend",
        "df": pd.DataFrame(
            {
                "Open": [99, 100, 101, 99, 103, 106, 109, 110, 111, 110, 109],
                "High": [100, 101, 102, 100, 105, 108, 111, 112, 111, 112, 112],
                "Low": [98, 99, 100, 98, 102, 105, 108, 108, 107, 108, 107],
                "Close": [99, 100, 101, 99, 104, 107, 110, 111, 110, 109, 110],
                "Volume": [500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510],
            }
        ),
        "expected": [
            Segment(
                Pre=[
                    Candle(high=100, low=98, open=99, close=99, volume=500),
                    Candle(high=101, low=99, open=100, close=100, volume=501),
                    Candle(high=102, low=100, open=101, close=101, volume=502),
                    Candle(high=100, low=98, open=99, close=99, volume=503),
                ],
                Trend=[
                    Candle(high=105, low=102, open=103, close=104, volume=504),
                    Candle(high=108, low=105, open=106, close=107, volume=505),
                    Candle(high=111, low=108, open=109, close=110, volume=506),
                    Candle(high=112, low=108, open=110, close=111, volume=507),
                    Candle(high=111, low=107, open=111, close=110, volume=508),
                ],
                Params=TradeParams(
                    direction=Direction.UP,
                    category=Category.WISHFUL,
                    profit=-1.0,
                    risk=2.0,
                    profit_risk_ratio=-50,
                    candles_num=2,
                ),
            )
        ],
    },
    {
        "name": "3. Uptrend with third candle stopping trend",
        "df": pd.DataFrame(
            {
                "Open": [99, 100, 101, 99, 103, 106, 109, 110, 111, 111, 109],
                "High": [100, 101, 102, 100, 105, 108, 111, 112, 112, 111, 112],
                "Low": [98, 99, 100, 98, 102, 105, 108, 108, 108, 107, 107],
                "Close": [99, 100, 101, 99, 104, 107, 110, 111, 111, 109, 108],
                "Volume": [500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510],
            }
        ),
        "expected": [
            Segment(
                Pre=[
                    Candle(high=100, low=98, open=99, close=99, volume=500),
                    Candle(high=101, low=99, open=100, close=100, volume=501),
                    Candle(high=102, low=100, open=101, close=101, volume=502),
                    Candle(high=100, low=98, open=99, close=99, volume=503),
                ],
                Trend=[
                    Candle(high=105, low=102, open=103, close=104, volume=504),
                    Candle(high=108, low=105, open=106, close=107, volume=505),
                    Candle(high=111, low=108, open=109, close=110, volume=506),
                    Candle(high=112, low=108, open=110, close=111, volume=507),
                    Candle(high=112, low=108, open=111, close=111, volume=508),
                ],
                Params=TradeParams(
                    direction=Direction.UP,
                    category=Category.WISHFUL,
                    profit=-1.0,
                    risk=2.0,
                    profit_risk_ratio=-50,
                    candles_num=2,
                ),
            )
        ],
    },
    {
        "name": "4. Downtrend. Trend ended with loss. Category LOSS. 2 candles in trend",
        "df": pd.DataFrame(
            {
                "Open": [114, 113, 112, 114, 114, 108, 105, 104, 105, 104, 105],
                "High": [115, 114, 113, 115, 114, 110, 106, 105, 106, 105, 106],
                "Low": [113, 112, 111, 113, 108, 104, 105, 104, 103, 104, 105],
                "Close": [114, 113, 112, 114, 108, 105, 106, 105, 106, 105, 106],
                "Volume": [600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610],
            }
        ),
        "expected": [
            Segment(
                Pre=[
                    Candle(high=115, low=113, open=114, close=114, volume=600),
                    Candle(high=114, low=112, open=113, close=113, volume=601),
                    Candle(high=113, low=111, open=112, close=112, volume=602),
                    Candle(high=115, low=113, open=114, close=114, volume=603),
                ],
                Trend=[
                    Candle(high=114, low=108, open=114, close=108, volume=604),
                    Candle(high=110, low=104, open=108, close=105, volume=605),
                    Candle(high=106, low=105, open=105, close=106, volume=606),
                ],
                Params=TradeParams(
                    direction=Direction.DOWN,
                    category=Category.BULL,
                    profit=1.0,
                    risk=0.0,
                    profit_risk_ratio=500,
                    candles_num=2,
                ),
            )
        ],
    },
    {
        "name": "5. Downtrend. Trend ended with loss. Category LOSS. 3 candles in trend",
        "df": pd.DataFrame(
            {
                "Open": [114, 113, 112, 114, 114, 108, 105, 104, 105, 104, 105],
                "High": [115, 114, 113, 115, 114, 110, 106, 107, 106, 105, 106],
                "Low": [113, 112, 111, 113, 108, 104, 103, 103, 103, 104, 105],
                "Close": [114, 113, 112, 114, 108, 105, 104, 106, 106, 105, 106],
                "Volume": [600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610],
            }
        ),
        "expected": [
            Segment(
                Pre=[
                    Candle(high=115, low=113, open=114, close=114, volume=600),
                    Candle(high=114, low=112, open=113, close=113, volume=601),
                    Candle(high=113, low=111, open=112, close=112, volume=602),
                    Candle(high=115, low=113, open=114, close=114, volume=603),
                ],
                Trend=[
                    Candle(high=114, low=108, open=114, close=108, volume=604),
                    Candle(high=110, low=104, open=108, close=105, volume=605),
                    Candle(high=106, low=103, open=105, close=104, volume=606),
                    Candle(high=107, low=103, open=104, close=106, volume=607),
                ],
                Params=TradeParams(
                    direction=Direction.DOWN,
                    category=Category.WISHFUL,
                    profit=-1.0,
                    risk=2.0,
                    profit_risk_ratio=-50,
                    candles_num=2,
                ),
            )
        ],
    },
    {
        "name": "6. Downtrend. Trend ended with profit. Category BEAR_POOR",
        "df": pd.DataFrame(
            {
                "Open": [114, 113, 112, 114, 114, 108, 105, 103, 105, 104, 105],
                "High": [115, 114, 113, 115, 114, 110, 106, 105, 106, 105, 106],
                "Low": [113, 112, 111, 113, 108, 104, 103, 102, 103, 104, 105],
                "Close": [114, 113, 112, 114, 108, 105, 103, 104, 106, 105, 106],
                "Volume": [600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610],
            }
        ),
        "expected": [
            Segment(
                Pre=[
                    Candle(high=115, low=113, open=114, close=114, volume=600),
                    Candle(high=114, low=112, open=113, close=113, volume=601),
                    Candle(high=113, low=111, open=112, close=112, volume=602),
                    Candle(high=115, low=113, open=114, close=114, volume=603),
                ],
                Trend=[
                    Candle(high=114, low=108, open=114, close=108, volume=604),
                    Candle(high=110, low=104, open=108, close=105, volume=605),
                    Candle(high=106, low=103, open=105, close=103, volume=606),
                    Candle(high=105, low=102, open=103, close=104, volume=607),
                ],
                Params=TradeParams(
                    direction=Direction.DOWN,
                    category=Category.WISHFUL,
                    profit=-2.0,
                    risk=2.0,
                    profit_risk_ratio=-100,
                    candles_num=2,
                ),
            )
        ],
    },
    {
        "name": "7. Downtrend. Trend ended with profit. Category BEAR_RICH",
        "df": pd.DataFrame(
            {
                "Open": [114, 113, 112, 114, 114, 108, 105, 100, 105, 104, 105],
                "High": [115, 114, 113, 115, 114, 110, 106, 102, 106, 105, 106],
                "Low": [113, 112, 111, 113, 108, 104, 99, 99, 103, 104, 105],
                "Close": [114, 113, 112, 114, 108, 105, 100, 101, 106, 105, 106],
                "Volume": [600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610],
            }
        ),
        "expected": [
            Segment(
                Pre=[
                    Candle(high=115, low=113, open=114, close=114, volume=600),
                    Candle(high=114, low=112, open=113, close=113, volume=601),
                    Candle(high=113, low=111, open=112, close=112, volume=602),
                    Candle(high=115, low=113, open=114, close=114, volume=603),
                ],
                Trend=[
                    Candle(high=114, low=108, open=114, close=108, volume=604),
                    Candle(high=110, low=104, open=108, close=105, volume=605),
                    Candle(high=106, low=99, open=105, close=100, volume=606),
                    Candle(high=102, low=99, open=100, close=101, volume=607),
                ],
                Params=TradeParams(
                    direction=Direction.DOWN,
                    category=Category.WISHFUL,
                    profit=-5.0,
                    risk=6.0,
                    profit_risk_ratio=-83.33,
                    candles_num=2,
                ),
            )
        ],
    },
    {
        "name": "8. Uptrend. Trend ended with loss. Category LOSS. 2 candles in trend",
        "df": pd.DataFrame(
            {
                "Open": [114, 113, 112, 114, 114, 115, 116, 104, 105, 104, 105],
                "High": [115, 114, 113, 115, 116, 117, 117, 105, 106, 105, 106],
                "Low": [113, 112, 111, 113, 113, 114, 114, 104, 103, 104, 105],
                "Close": [114, 113, 112, 114, 115, 116, 115, 105, 106, 105, 106],
                "Volume": [600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610],
            }
        ),
        "expected": [
            Segment(
                Pre=[
                    Candle(high=115, low=113, open=114, close=114, volume=600),
                    Candle(high=114, low=112, open=113, close=113, volume=601),
                    Candle(high=113, low=111, open=112, close=112, volume=602),
                    Candle(high=115, low=113, open=114, close=114, volume=603),
                ],
                Trend=[
                    Candle(high=116, low=113, open=114, close=115, volume=604),
                    Candle(high=117, low=114, open=115, close=116, volume=605),
                    Candle(high=117, low=114, open=116, close=115, volume=606),
                ],
                Params=TradeParams(
                    direction=Direction.UP,
                    category=Category.BEAR,
                    profit=1.0,
                    risk=1.0,
                    profit_risk_ratio=100,
                    candles_num=2,
                ),
            )
        ],
    },
    {
        "name": "9. Uptrend. Trend ended with loss. Category LOSS. 3 candles in trend",
        "df": pd.DataFrame(
            {
                "Open": [114, 113, 112, 114, 114, 115, 116, 117, 105, 104, 105],
                "High": [115, 114, 113, 115, 116, 117, 118, 118, 106, 105, 106],
                "Low": [113, 112, 111, 113, 113, 114, 115, 114, 103, 104, 105],
                "Close": [114, 113, 112, 114, 115, 116, 117, 115, 106, 105, 106],
                "Volume": [600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610],
            }
        ),
        "expected": [
            Segment(
                Pre=[
                    Candle(high=115, low=113, open=114, close=114, volume=600),
                    Candle(high=114, low=112, open=113, close=113, volume=601),
                    Candle(high=113, low=111, open=112, close=112, volume=602),
                    Candle(high=115, low=113, open=114, close=114, volume=603),
                ],
                Trend=[
                    Candle(high=116, low=113, open=114, close=115, volume=604),
                    Candle(high=117, low=114, open=115, close=116, volume=605),
                    Candle(high=118, low=115, open=116, close=117, volume=606),
                    Candle(high=118, low=114, open=117, close=115, volume=607),
                ],
                Params=TradeParams(
                    direction=Direction.UP,
                    category=Category.WISHFUL,
                    profit=-1.0,
                    risk=2.0,
                    profit_risk_ratio=-50,
                    candles_num=2,
                ),
            )
        ],
    },
    {
        "name": "10. Uptrend. Trend ended with profit. Category BEAR_POOR.",
        "df": pd.DataFrame(
            {
                "Open": [114, 113, 112, 114, 114, 115, 116, 118, 105, 104, 105],
                "High": [115, 114, 113, 115, 116, 117, 118, 119, 106, 105, 106],
                "Low": [113, 112, 111, 113, 113, 114, 115, 116, 103, 104, 105],
                "Close": [114, 113, 112, 114, 115, 116, 118, 117, 106, 105, 106],
                "Volume": [600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610],
            }
        ),
        "expected": [
            Segment(
                Pre=[
                    Candle(high=115, low=113, open=114, close=114, volume=600),
                    Candle(high=114, low=112, open=113, close=113, volume=601),
                    Candle(high=113, low=111, open=112, close=112, volume=602),
                    Candle(high=115, low=113, open=114, close=114, volume=603),
                ],
                Trend=[
                    Candle(high=116, low=113, open=114, close=115, volume=604),
                    Candle(high=117, low=114, open=115, close=116, volume=605),
                    Candle(high=118, low=115, open=116, close=118, volume=606),
                    Candle(high=119, low=116, open=118, close=117, volume=607),
                ],
                Params=TradeParams(
                    direction=Direction.UP,
                    category=Category.WISHFUL,
                    profit=-2.0,
                    risk=2.0,
                    profit_risk_ratio=-100,
                    candles_num=2,
                ),
            )
        ],
    },
    {
        "name": "11. Uptrend. Trend ended with profit. Category BEAR_RICH.",
        "df": pd.DataFrame(
            {
                "Open": [114, 113, 112, 114, 114, 115, 116, 121, 105, 104, 105],
                "High": [115, 114, 113, 115, 116, 117, 122, 122, 106, 105, 106],
                "Low": [113, 112, 111, 113, 113, 114, 115, 119, 103, 104, 105],
                "Close": [114, 113, 112, 114, 115, 116, 121, 120, 106, 105, 106],
                "Volume": [600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610],
            }
        ),
        "expected": [
            Segment(
                Pre=[
                    Candle(high=115, low=113, open=114, close=114, volume=600),
                    Candle(high=114, low=112, open=113, close=113, volume=601),
                    Candle(high=113, low=111, open=112, close=112, volume=602),
                    Candle(high=115, low=113, open=114, close=114, volume=603),
                ],
                Trend=[
                    Candle(high=116, low=113, open=114, close=115, volume=604),
                    Candle(high=117, low=114, open=115, close=116, volume=605),
                    Candle(high=122, low=115, open=116, close=121, volume=606),
                    Candle(high=122, low=119, open=121, close=120, volume=607),
                ],
                Params=TradeParams(
                    direction=Direction.UP,
                    category=Category.WISHFUL,
                    profit=-5.0,
                    risk=6.0,
                    profit_risk_ratio=-83.33,
                    candles_num=2,
                ),
            )
        ],
    },
    {
        "name": "12. Downtrend with third candle stopping trend",
        "df": pd.DataFrame(
            {
                "Open": [114, 113, 112, 114, 114, 108, 105, 102, 102, 102, 103],
                "High": [115, 114, 113, 115, 114, 110, 106, 103, 103, 104, 104],
                "Low": [113, 112, 111, 113, 108, 104, 102, 101, 101, 102, 102],
                "Close": [114, 113, 112, 114, 108, 105, 102, 102, 102, 103, 103],
                "Volume": [500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510],
            }
        ),
        "expected": [
            Segment(
                Pre=[
                    Candle(high=115, low=113, open=114, close=114, volume=500),
                    Candle(high=114, low=112, open=113, close=113, volume=501),
                    Candle(high=113, low=111, open=112, close=112, volume=502),
                    Candle(high=115, low=113, open=114, close=114, volume=503),
                ],
                Trend=[
                    Candle(high=114, low=108, open=114, close=108, volume=504),
                    Candle(high=110, low=104, open=108, close=105, volume=505),
                    Candle(high=106, low=102, open=105, close=102, volume=506),
                    Candle(high=103, low=101, open=102, close=102, volume=507),
                ],
                Params=TradeParams(
                    direction=Direction.DOWN,
                    category=Category.WISHFUL,
                    profit=-3.0,
                    risk=3.0,
                    profit_risk_ratio=-100,
                    candles_num=2,
                ),
            )
        ],
    },
    {
        "name": "13. Uptrend followed by immediate downtrend with clear end",
        "df": pd.DataFrame(
            {
                "Open": [99, 100, 101, 99, 103, 106, 109, 111, 110, 107, 105, 104, 106],
                "High": [
                    100,
                    101,
                    102,
                    100,
                    105,
                    108,
                    111,
                    112,
                    111,
                    108,
                    106,
                    106,
                    108,
                ],
                "Low": [98, 99, 100, 98, 102, 105, 108, 108, 106, 103, 102, 103, 105],
                "Close": [
                    99,
                    100,
                    101,
                    99,
                    104,
                    107,
                    110,
                    110,
                    107,
                    105,
                    103,
                    105,
                    107,
                ],
                "Volume": [
                    500,
                    501,
                    502,
                    503,
                    504,
                    505,
                    506,
                    507,
                    508,
                    509,
                    510,
                    511,
                    512,
                ],
            }
        ),
        "expected": [
            Segment(
                Pre=[
                    Candle(high=100, low=98, open=99, close=99, volume=500),
                    Candle(high=101, low=99, open=100, close=100, volume=501),
                    Candle(high=102, low=100, open=101, close=101, volume=502),
                    Candle(high=100, low=98, open=99, close=99, volume=503),
                ],
                Trend=[
                    Candle(high=105, low=102, open=103, close=104, volume=504),
                    Candle(high=108, low=105, open=106, close=107, volume=505),
                    Candle(high=111, low=108, open=109, close=110, volume=506),
                    Candle(high=112, low=108, open=111, close=110, volume=507),
                ],
                Params=TradeParams(
                    direction=Direction.UP,
                    category=Category.WISHFUL,
                    profit=-1.0,
                    risk=2.0,
                    profit_risk_ratio=-50,
                    candles_num=2,
                ),
            ),
            Segment(
                Pre=[
                    Candle(high=105, low=102, open=103, close=104, volume=504),
                    Candle(high=108, low=105, open=106, close=107, volume=505),
                    Candle(high=111, low=108, open=109, close=110, volume=506),
                    Candle(high=112, low=108, open=111, close=110, volume=507),
                ],
                Trend=[
                    Candle(high=111, low=106, open=110, close=107, volume=508),
                    Candle(high=108, low=103, open=107, close=105, volume=509),
                    Candle(high=106, low=102, open=105, close=103, volume=510),
                    Candle(high=106, low=103, open=104, close=105, volume=511),
                ],
                Params=TradeParams(
                    direction=Direction.DOWN,
                    category=Category.WISHFUL,
                    profit=-2.0,
                    risk=3.0,
                    profit_risk_ratio=-66.67,
                    candles_num=2,
                ),
            ),
        ],
    },
    {
        "name": "14. Two uptrends with BEARISH_REV_REV candle in between",
        "df": pd.DataFrame(
            {
                "Open": [
                    99.0,
                    100.0,
                    101.0,
                    99.0,
                    103.0,
                    106.0,
                    109.0,
                    108.0,
                    110.0,
                    113.0,
                    116.0,
                    118.0,
                    116.0,
                ],
                "High": [
                    100.0,
                    101.0,
                    102.0,
                    100.0,
                    105.0,
                    108.0,
                    111.0,
                    109.0,
                    112.0,
                    115.0,
                    118.0,
                    119.0,
                    118.0,
                ],
                "Low": [
                    98.0,
                    99.0,
                    100.0,
                    98.0,
                    102.0,
                    105.0,
                    108.0,
                    106.0,
                    109.0,
                    112.0,
                    115.0,
                    115.0,
                    115.0,
                ],
                "Close": [
                    99.0,
                    100.0,
                    101.0,
                    99.0,
                    104.0,
                    107.0,
                    110.0,
                    107.0,
                    111.0,
                    114.0,
                    117.0,
                    116.0,
                    117.0,
                ],
                "Volume": [
                    1000,
                    1001,
                    1002,
                    1003,
                    1004,
                    1005,
                    1006,
                    1007,
                    1008,
                    1009,
                    1010,
                    1011,
                    1012,
                ],
            }
        ),
        "expected": [
            Segment(
                Pre=[
                    Candle(high=100, low=98, open=99, close=99, volume=1000),
                    Candle(high=101, low=99, open=100, close=100, volume=1001),
                    Candle(high=102, low=100, open=101, close=101, volume=1002),
                    Candle(high=100, low=98, open=99, close=99, volume=1003),
                ],
                Trend=[
                    Candle(high=105, low=102, open=103, close=104, volume=1004),
                    Candle(high=108, low=105, open=106, close=107, volume=1005),
                    Candle(high=111, low=108, open=109, close=110, volume=1006),
                    Candle(high=109, low=106, open=108, close=107, volume=1007),
                ],
                Params=TradeParams(
                    direction=Direction.UP,
                    category=Category.WISHFUL,
                    profit=-1.0,
                    risk=2.0,
                    profit_risk_ratio=-50,
                    candles_num=2,
                ),
            ),
            Segment(
                Pre=[
                    Candle(high=105, low=102, open=103, close=104, volume=1004),
                    Candle(high=108, low=105, open=106, close=107, volume=1005),
                    Candle(high=111, low=108, open=109, close=110, volume=1006),
                    Candle(high=109, low=106, open=108, close=107, volume=1007),
                ],
                Trend=[
                    Candle(high=112, low=109, open=110, close=111, volume=1008),
                    Candle(high=115, low=112, open=113, close=114, volume=1009),
                    Candle(high=118, low=115, open=116, close=117, volume=1010),
                    Candle(high=119, low=115, open=118, close=116, volume=1011),
                ],
                Params=TradeParams(
                    direction=Direction.UP,
                    category=Category.WISHFUL,
                    profit=-1.0,
                    risk=2.0,
                    profit_risk_ratio=-50,
                    candles_num=2,
                ),
            ),
        ],
    },
    {
        "name": "15. Downtrend followed by immediate uptrend with clear end",
        "df": pd.DataFrame(
            {
                "Open": [
                    111.0,
                    112.0,
                    113.0,
                    112.0,
                    112.0,
                    109.0,
                    107.0,
                    101.0,
                    104.0,
                    107.0,
                    110.0,
                    109.0,
                    109.0,
                ],
                "High": [
                    112.0,
                    113.0,
                    114.0,
                    113.0,
                    113.0,
                    110.0,
                    108.0,
                    103.0,
                    106.0,
                    109.0,
                    112.0,
                    110.0,
                    111.0,
                ],
                "Low": [
                    110.0,
                    111.0,
                    112.0,
                    111.0,
                    108.0,
                    106.0,
                    104.0,
                    100.0,
                    103.0,
                    106.0,
                    109.0,
                    107.0,
                    108.0,
                ],
                "Close": [
                    111.0,
                    112.0,
                    113.0,
                    112.0,
                    109.0,
                    107.0,
                    105.0,
                    102.0,
                    105.0,
                    108.0,
                    111.0,
                    108.0,
                    108.0,
                ],
                "Volume": [
                    1000,
                    1001,
                    1002,
                    1003,
                    1004,
                    1005,
                    1006,
                    1007,
                    1008,
                    1009,
                    1010,
                    1011,
                    1012,
                ],
            }
        ),
        "expected": [
            Segment(
                Pre=[
                    Candle(high=112, low=110, open=111, close=111, volume=1000),
                    Candle(high=113, low=111, open=112, close=112, volume=1001),
                    Candle(high=114, low=112, open=113, close=113, volume=1002),
                    Candle(high=113, low=111, open=112, close=112, volume=1003),
                ],
                Trend=[
                    Candle(high=113, low=108, open=112, close=109, volume=1004),
                    Candle(high=110, low=106, open=109, close=107, volume=1005),
                    Candle(high=108, low=104, open=107, close=105, volume=1006),
                    Candle(high=103, low=100, open=101, close=102, volume=1007),
                ],
                Params=TradeParams(
                    direction=Direction.DOWN,
                    category=Category.WISHFUL,
                    profit=-2.0,
                    risk=3.0,
                    profit_risk_ratio=-66.67,
                    candles_num=2,
                ),
            ),
            Segment(
                Pre=[
                    Candle(high=113, low=108, open=112, close=109, volume=1004),
                    Candle(high=110, low=106, open=109, close=107, volume=1005),
                    Candle(high=108, low=104, open=107, close=105, volume=1006),
                    Candle(high=103, low=100, open=101, close=102, volume=1007),
                ],
                Trend=[
                    Candle(high=106, low=103, open=104, close=105, volume=1008),
                    Candle(high=109, low=106, open=107, close=108, volume=1009),
                    Candle(high=112, low=109, open=110, close=111, volume=1010),
                    Candle(high=110, low=107, open=109, close=108, volume=1011),
                ],
                Params=TradeParams(
                    direction=Direction.UP,
                    category=Category.WISHFUL,
                    profit=-1.0,
                    risk=2.0,
                    profit_risk_ratio=-50,
                    candles_num=2,
                ),
            ),
        ],
    },
    {
        "name": "16. Two downtrends with BULLISH_REV candle in between",
        "df": pd.DataFrame(
            {
                "Open": [
                    119.0,
                    120.0,
                    121.0,
                    120.0,
                    117.0,
                    116.0,
                    113.0,
                    111.0,
                    112.0,
                    109.0,
                    107.0,
                    106.0,
                    106.0,
                ],
                "High": [
                    120.0,
                    121.0,
                    122.0,
                    121.0,
                    118.0,
                    117.0,
                    114.0,
                    114.0,
                    113.0,
                    110.0,
                    108.0,
                    107.0,
                    108.0,
                ],
                "Low": [
                    118.0,
                    119.0,
                    120.0,
                    119.0,
                    115.0,
                    112.0,
                    109.0,
                    110.0,
                    110.0,
                    107.0,
                    105.0,
                    104.0,
                    105.0,
                ],
                "Close": [
                    119.0,
                    120.0,
                    121.0,
                    120.0,
                    116.0,
                    113.0,
                    110.0,
                    113.0,
                    111.0,
                    108.0,
                    106.0,
                    105.0,
                    107.0,
                ],
                "Volume": [
                    1000,
                    1001,
                    1002,
                    1003,
                    1004,
                    1005,
                    1006,
                    1007,
                    1008,
                    1009,
                    1010,
                    1011,
                    1012,
                ],
            }
        ),
        "expected": [
            Segment(
                Pre=[
                    Candle(high=120, low=118, open=119, close=119, volume=1000),
                    Candle(high=121, low=119, open=120, close=120, volume=1001),
                    Candle(high=122, low=120, open=121, close=121, volume=1002),
                    Candle(high=121, low=119, open=120, close=120, volume=1003),
                ],
                Trend=[
                    Candle(high=118, low=115, open=117, close=116, volume=1004),
                    Candle(high=117, low=112, open=116, close=113, volume=1005),
                    Candle(high=114, low=109, open=113, close=110, volume=1006),
                    Candle(high=114, low=110, open=111, close=113, volume=1007),
                ],
                Params=TradeParams(
                    direction=Direction.DOWN,
                    category=Category.WISHFUL,
                    profit=-3.0,
                    risk=4.0,
                    profit_risk_ratio=-75,
                    candles_num=2,
                ),
            ),
            Segment(
                Pre=[
                    Candle(high=118, low=115, open=117, close=116, volume=1004),
                    Candle(high=117, low=112, open=116, close=113, volume=1005),
                    Candle(high=114, low=109, open=113, close=110, volume=1006),
                    Candle(high=114, low=110, open=111, close=113, volume=1007),
                ],
                Trend=[
                    Candle(high=113, low=110, open=112, close=111, volume=1008),
                    Candle(high=110, low=107, open=109, close=108, volume=1009),
                    Candle(high=108, low=105, open=107, close=106, volume=1010),
                    Candle(high=107, low=104, open=106, close=105, volume=1011),
                    Candle(high=108, low=105, open=106, close=107, volume=1012),
                ],
                Params=TradeParams(
                    direction=Direction.DOWN,
                    category=Category.WISHFUL,
                    profit=-1.0,
                    risk=2.0,
                    profit_risk_ratio=-50,
                    candles_num=2,
                ),
            ),
        ],
    },
]


@pytest.mark.parametrize("case", test_cases, ids=[c["name"] for c in test_cases])
def test_marker(case):
    case["df"].columns = case["df"].columns.str.lower()
    estimator = ReversalEstimator()
    marker = Marker(estimator=estimator, a_len=4)
    result = marker.mark(case["df"])
    for segment_idx, segment_val in enumerate(result):
        # Compare Pre candles
        for idx, candle in enumerate(segment_val.Pre):
            want_candle = case["expected"][segment_idx].Pre[idx]
            assert (
                candle.high == want_candle.high
            ), f"Pre candle high mismatch in case {case['name']} at index {idx}"
            assert (
                candle.low == want_candle.low
            ), f"Pre candle low mismatch in case {case['name']} at index {idx}"
            assert (
                candle.open == want_candle.open
            ), f"Pre candle open mismatch in case {case['name']} at index {idx}"
            assert (
                candle.close == want_candle.close
            ), f"Pre candle close mismatch in case {case['name']} at index {idx}"
            assert (
                candle.volume == want_candle.volume
            ), f"Pre candle volume mismatch in case {case['name']} at index {idx}"

        # Compare Trend candles
        for idx, candle in enumerate(segment_val.Trend):
            assert (
                candle.high == case["expected"][segment_idx].Trend[idx].high
            ), f"Trend candle high mismatch in case {case['name']} at index {idx}"
            assert (
                candle.low == case["expected"][segment_idx].Trend[idx].low
            ), f"Trend candle low mismatch in case {case['name']} at index {idx}"
            assert (
                candle.open == case["expected"][segment_idx].Trend[idx].open
            ), f"Trend candle open mismatch in case {case['name']} at index {idx}"
            assert (
                candle.close == case["expected"][segment_idx].Trend[idx].close
            ), f"Trend candle close mismatch in case {case['name']} at index {idx}"
            assert (
                candle.volume == case["expected"][segment_idx].Trend[idx].volume
            ), f"Trend candle volume mismatch in case {case['name']} at index {idx}"

        # Compare Params
        assert (
            segment_val.Params.direction
            == case["expected"][segment_idx].Params.direction
        ), f"Direction mismatch in case {case['name']}"

        assert (
            segment_val.Params.category == case["expected"][segment_idx].Params.category
        ), f"Category mismatch in case {case['name']}"

        assert round(segment_val.Params.profit, 2) == round(
            case["expected"][segment_idx].Params.profit, 2
        ), f"Profit mismatch in case {case['name']}"

        assert round(segment_val.Params.risk, 2) == round(
            case["expected"][segment_idx].Params.risk, 2
        ), f"Risk mismatch in case {case['name']}"

        assert round(segment_val.Params.profit_risk_ratio, 2) == round(
            case["expected"][segment_idx].Params.profit_risk_ratio, 2
        ), f"Profit/Risk ratio mismatch in case {case['name']}"
