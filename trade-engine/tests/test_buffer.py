import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import pytest

from domain.types.candle import Candle
from services.buffer.buffer import Buffer

get_candle_test_cases = [
    {
        "name": "0. Get candle from high timeframe from index 0",
        "low_df": pd.DataFrame(),
        "high_df": pd.DataFrame(
            {
                "Open": [100, 105],
                "High": [110, 115],
                "Low": [90, 95],
                "Close": [105, 110],
                "Volume": [500, 600],
                "Close time": [
                    "2024-01-01 01:09:04.99",
                    "2024-01-01 01:09:09.99",
                ],
            },
            index=pd.to_datetime(["2024-01-01 01:09:05", "2024-01-01 01:09:10"]),
        ),
        "tf": "high",
        "low_index": 0,
        "high_index": 0,
        "expected_candle": Candle(
            open=100,
            high=110,
            low=90,
            close=105,
            volume=500,
            close_time=pd.Timestamp("2024-01-01 01:09:05"),
        ),
        "expected_low_index": 4,
        "expected_high_index": 1,
        "expected_error": "",
    },
    {
        "name": "1. Get candle from high timeframe from index 1",
        "low_df": pd.DataFrame(),
        "high_df": pd.DataFrame(
            {
                "Open": [100, 105],
                "High": [110, 115],
                "Low": [90, 95],
                "Close": [105, 110],
                "Volume": [500, 600],
                "Close time": [
                    "2024-01-01 01:09:04.99",
                    "2024-01-01 01:09:09.99",
                ],
            },
            index=pd.to_datetime(["2024-01-01 01:09:05", "2024-01-01 01:09:10"]),
        ),
        "tf": "high",
        "low_index": 0,
        "high_index": 1,
        "expected_candle": Candle(
            open=105,
            high=115,
            low=95,
            close=110,
            volume=600,
            close_time=pd.Timestamp("2024-01-01 01:09:10"),
        ),
        "expected_low_index": 9,
        "expected_high_index": 2,
        "expected_error": "",
    },
    {
        "name": "2. Get candle from high timeframe from index that exceeds dataframe length",
        "low_df": pd.DataFrame(),
        "high_df": pd.DataFrame(
            {
                "Open": [100, 105],
                "High": [110, 115],
                "Low": [90, 95],
                "Close": [105, 110],
                "Volume": [500, 600],
                "Close time": [
                    "2024-01-01 01:09:04.99",
                    "2024-01-01 01:09:09.99",
                ],
            },
            index=pd.to_datetime(["2024-01-01 01:09:05", "2024-01-01 01:09:10"]),
        ),
        "tf": "high",
        "low_index": 9,
        "high_index": 2,
        "expected_candle": Candle(
            open=0,
            high=0,
            low=0,
            close=0,
            volume=0,
            close_time=pd.Timestamp("1970-01-01"),
        ),
        "expected_low_index": 9,
        "expected_high_index": 2,
        "expected_error": "high_index 2 out of range for 2 rows",
    },
    {
        "name": "3. Get candle from low timeframe from index 0",
        "low_df": pd.DataFrame(
            {
                "Open": [100, 102, 104, 106, 105, 105, 107, 109, 111, 110],
                "High": [102, 104, 106, 110, 107, 107, 109, 111, 115, 112],
                "Low": [99, 90, 103, 105, 104, 104, 95, 108, 110, 109],
                "Close": [102, 104, 106, 107, 105, 109, 111, 110, 112, 110],
                "Volume": [100, 100, 100, 100, 100, 120, 120, 120, 120, 120],
                "Close time": [
                    "2024-01-01 01:09:00.99",
                    "2024-01-01 01:09:01.99",
                    "2024-01-01 01:09:02.99",
                    "2024-01-01 01:09:03.99",
                    "2024-01-01 01:09:04.99",
                    "2024-01-01 01:09:05.99",
                    "2024-01-01 01:09:06.99",
                    "2024-01-01 01:09:07.99",
                    "2024-01-01 01:09:08.99",
                    "2024-01-01 01:09:09.99",
                ],
            },
            index=pd.to_datetime(
                [
                    "2024-01-01 09:01",
                    "2024-01-01 09:02",
                    "2024-01-01 09:03",
                    "2024-01-01 09:04",
                    "2024-01-01 09:05",
                    "2024-01-01 09:06",
                    "2024-01-01 09:07",
                    "2024-01-01 09:08",
                    "2024-01-01 09:09",
                    "2024-01-01 09:10",
                ]
            ),
        ),
        "high_df": pd.DataFrame(
            {
                "Open": [100, 105],
                "High": [110, 115],
                "Low": [90, 95],
                "Close": [105, 110],
                "Volume": [500, 600],
            },
            index=pd.to_datetime(["2024-01-01 09:05", "2024-01-01 09:10"]),
        ),
        "tf": "low",
        "low_index": 0,
        "high_index": 0,
        "expected_candle": Candle(
            open=100,
            high=102,
            low=99,
            close=102,
            volume=100,
            close_time=pd.Timestamp("2024-01-01 01:09:01"),
        ),
        "expected_low_index": 1,
        "expected_high_index": 1,
        "expected_error": "",
    },
    {
        "name": "4. Get candle from low timeframe from index 2",
        "low_df": pd.DataFrame(
            {
                "Open": [100, 102, 104, 106, 105, 105, 107, 109, 111, 110],
                "High": [102, 104, 106, 110, 107, 107, 109, 111, 115, 112],
                "Low": [99, 90, 103, 105, 104, 104, 95, 108, 110, 109],
                "Close": [102, 104, 106, 107, 105, 109, 111, 110, 112, 110],
                "Volume": [100, 100, 100, 100, 100, 120, 120, 120, 120, 120],
                "Close time": [
                    "2024-01-01 01:09:00.99",
                    "2024-01-01 01:09:01.99",
                    "2024-01-01 01:09:02.99",
                    "2024-01-01 01:09:03.99",
                    "2024-01-01 01:09:04.99",
                    "2024-01-01 01:09:05.99",
                    "2024-01-01 01:09:06.99",
                    "2024-01-01 01:09:07.99",
                    "2024-01-01 01:09:08.99",
                    "2024-01-01 01:09:09.99",
                ],
            },
            index=pd.to_datetime(
                [
                    "2024-01-01 09:01",
                    "2024-01-01 09:02",
                    "2024-01-01 09:03",
                    "2024-01-01 09:04",
                    "2024-01-01 09:05",
                    "2024-01-01 09:06",
                    "2024-01-01 09:07",
                    "2024-01-01 09:08",
                    "2024-01-01 09:09",
                    "2024-01-01 09:10",
                ]
            ),
        ),
        "high_df": pd.DataFrame(
            {
                "Open": [100, 105],
                "High": [110, 115],
                "Low": [90, 95],
                "Close": [105, 110],
                "Volume": [500, 600],
            },
            index=pd.to_datetime(["2024-01-01 09:05", "2024-01-01 09:10"]),
        ),
        "tf": "low",
        "low_index": 2,
        "high_index": 1,
        "expected_candle": Candle(
            open=104,
            high=106,
            low=103,
            close=106,
            volume=100,
            close_time=pd.Timestamp(
                "2024-01-01 01:09:03",
            ),
        ),
        "expected_low_index": 3,
        "expected_high_index": 1,
        "expected_error": "",
    },
    {
        "name": "5. Get candle from low timeframe from index 4",
        "low_df": pd.DataFrame(
            {
                "Open": [100, 102, 104, 106, 105, 105, 107, 109, 111, 110],
                "High": [102, 104, 106, 110, 107, 107, 109, 111, 115, 112],
                "Low": [99, 90, 103, 105, 104, 104, 95, 108, 110, 109],
                "Close": [102, 104, 106, 107, 105, 109, 111, 110, 112, 110],
                "Volume": [100, 100, 100, 100, 100, 120, 120, 120, 120, 120],
                "Close time": [
                    "2024-01-01 01:09:00.99",
                    "2024-01-01 01:09:01.99",
                    "2024-01-01 01:09:02.99",
                    "2024-01-01 01:09:03.99",
                    "2024-01-01 01:09:04.99",
                    "2024-01-01 01:09:05.99",
                    "2024-01-01 01:09:06.99",
                    "2024-01-01 01:09:07.99",
                    "2024-01-01 01:09:08.99",
                    "2024-01-01 01:09:09.99",
                ],
            },
            index=pd.to_datetime(
                [
                    "2024-01-01 09:01",
                    "2024-01-01 09:02",
                    "2024-01-01 09:03",
                    "2024-01-01 09:04",
                    "2024-01-01 09:05",
                    "2024-01-01 09:06",
                    "2024-01-01 09:07",
                    "2024-01-01 09:08",
                    "2024-01-01 09:09",
                    "2024-01-01 09:10",
                ]
            ),
        ),
        "high_df": pd.DataFrame(
            {
                "Open": [100, 105],
                "High": [110, 115],
                "Low": [90, 95],
                "Close": [105, 110],
                "Volume": [500, 600],
            },
            index=pd.to_datetime(["2024-01-01 09:05", "2024-01-01 09:10"]),
        ),
        "tf": "low",
        "low_index": 4,
        "high_index": 1,
        "expected_candle": Candle(
            open=105,
            high=107,
            low=104,
            close=105,
            volume=100,
            close_time=pd.Timestamp(
                "2024-01-01 01:09:05",
            ),
        ),
        "expected_low_index": 5,
        "expected_high_index": 2,
        "expected_error": "",
    },
    {
        "name": "6. Get candle from low timeframe from index that exceeds dataframe length",
        "low_df": pd.DataFrame(
            {
                "Open": [100, 102, 104, 106, 105, 105, 107, 109, 111, 110],
                "High": [102, 104, 106, 110, 107, 107, 109, 111, 115, 112],
                "Low": [99, 90, 103, 105, 104, 104, 95, 108, 110, 109],
                "Close": [102, 104, 106, 107, 105, 109, 111, 110, 112, 110],
                "Volume": [100, 100, 100, 100, 100, 120, 120, 120, 120, 120],
                "Close time": [
                    "2024-01-01 01:09:00.99",
                    "2024-01-01 01:09:01.99",
                    "2024-01-01 01:09:02.99",
                    "2024-01-01 01:09:03.99",
                    "2024-01-01 01:09:04.99",
                    "2024-01-01 01:09:05.99",
                    "2024-01-01 01:09:06.99",
                    "2024-01-01 01:09:07.99",
                    "2024-01-01 01:09:08.99",
                    "2024-01-01 01:09:09.99",
                ],
            },
            index=pd.to_datetime(
                [
                    "2024-01-01 09:01",
                    "2024-01-01 09:02",
                    "2024-01-01 09:03",
                    "2024-01-01 09:04",
                    "2024-01-01 09:05",
                    "2024-01-01 09:06",
                    "2024-01-01 09:07",
                    "2024-01-01 09:08",
                    "2024-01-01 09:09",
                    "2024-01-01 09:10",
                ]
            ),
        ),
        "high_df": pd.DataFrame(
            {
                "Open": [100, 105],
                "High": [110, 115],
                "Low": [90, 95],
                "Close": [105, 110],
                "Volume": [500, 600],
            },
            index=pd.to_datetime(["2024-01-01 09:05", "2024-01-01 09:10"]),
        ),
        "tf": "low",
        "low_index": 10,
        "high_index": 3,
        "expected_candle": Candle(
            open=0,
            high=0,
            low=0,
            close=0,
            volume=0,
            close_time=pd.Timestamp("1970-01-01"),
        ),
        "expected_low_index": 10,
        "expected_high_index": 3,
        "expected_error": "low_index 10 out of range for 10 rows",
    },
]


@pytest.mark.parametrize(
    "case", get_candle_test_cases, ids=[c["name"] for c in get_candle_test_cases]
)
def test_get_candle(case):
    # INITIALIZATION

    buffer = Buffer(
        low_df=case["low_df"],
        high_df=case["high_df"],
        low_index=case["low_index"],
        high_index=case["high_index"],
    )
    buffer.set_tf(case["tf"])

    candle = Candle(
        open=0,
        high=0,
        low=0,
        close=0,
        volume=0,
        close_time=pd.Timestamp("1970-01-01"),
    )

    # EXECUTION

    match True:
        case _ if len(case["expected_error"]) == 0:
            candle = buffer.get_candle()
        case _:
            with pytest.raises(IndexError, match=case["expected_error"] or r"^$"):
                candle = buffer.get_candle()

    # ASSERTIONS

    assert candle == case["expected_candle"]

    assert buffer.low_index == case["expected_low_index"]

    assert buffer.high_index == case["expected_high_index"]
