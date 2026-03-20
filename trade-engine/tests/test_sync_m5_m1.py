import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import pytest

from utils.sync_m5_m1 import Tolerances, sync_m5_m1

sync_test_cases = [
    {
        "name": "0. All candles present, exact match",
        "m5": pd.DataFrame(
            {
                "Open": [100, 105],
                "High": [110, 115],
                "Low": [90, 95],
                "Close": [105, 110],
                "Volume": [500, 600],
            },
            index=pd.to_datetime(["2024-01-01 09:05", "2024-01-01 09:10"]),
        ),
        "m1": pd.DataFrame(
            {
                "Open": [100, 102, 104, 106, 105, 105, 107, 109, 111, 110],
                "High": [102, 104, 106, 110, 107, 107, 109, 111, 115, 112],
                "Low": [99, 90, 103, 105, 104, 104, 95, 108, 110, 109],
                "Close": [102, 104, 106, 107, 105, 109, 111, 110, 112, 110],
                "Volume": [100, 100, 100, 100, 100, 120, 120, 120, 120, 120],
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
        "tol": Tolerances(
            eps_price=1e-5,
            eps_vol=1e-5,
        ),
        "expected_m5": pd.DataFrame(
            {
                "Open": [100, 105],
                "High": [110, 115],
                "Low": [90, 95],
                "Close": [105, 110],
                "Volume": [500, 600],
            },
            index=pd.to_datetime(["2024-01-01 09:05", "2024-01-01 09:10"]),
        ),
        "expected_m1": pd.DataFrame(
            {
                "Open": [100, 102, 104, 106, 105, 105, 107, 109, 111, 110],
                "High": [102, 104, 106, 110, 107, 107, 109, 111, 115, 112],
                "Low": [99, 90, 103, 105, 104, 104, 95, 108, 110, 109],
                "Close": [102, 104, 106, 107, 105, 109, 111, 110, 112, 110],
                "Volume": [100, 100, 100, 100, 100, 120, 120, 120, 120, 120],
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
        "expected_report": pd.DataFrame(
            {
                "Status": ["OK", "OK"],
            },
            index=pd.to_datetime(["2024-01-01 09:05", "2024-01-01 09:10"]),
        ),
    },
    {
        "name": "1. One m1 candle absent, exact match",
        "m5": pd.DataFrame(
            {
                "Open": [100, 105],
                "High": [110, 115],
                "Low": [90, 95],
                "Close": [105, 110],
                "Volume": [500, 600],
            },
            index=pd.to_datetime(["2024-01-01 09:05", "2024-01-01 09:10"]),
        ),
        "m1": pd.DataFrame(
            {
                "Open": [100, 102, 104, 106, 105, 105, 107, 109, 111],
                "High": [102, 104, 106, 110, 107, 107, 109, 111, 115],
                "Low": [99, 90, 103, 105, 104, 104, 95, 108, 110],
                "Close": [102, 104, 106, 107, 105, 109, 111, 110, 112],
                "Volume": [100, 100, 100, 100, 100, 120, 120, 120, 120],
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
                ]
            ),
        ),
        "tol": Tolerances(
            eps_price=1e-5,
            eps_vol=1e-5,
        ),
        "expected_m5": pd.DataFrame(
            {
                "Open": [100],
                "High": [110],
                "Low": [90],
                "Close": [105],
                "Volume": [500],
            },
            index=pd.to_datetime(["2024-01-01 09:05"]),
        ),
        "expected_m1": pd.DataFrame(
            {
                "Open": [100, 102, 104, 106, 105],
                "High": [102, 104, 106, 110, 107],
                "Low": [99, 90, 103, 105, 104],
                "Close": [102, 104, 106, 107, 105],
                "Volume": [100, 100, 100, 100, 100],
            },
            index=pd.to_datetime(
                [
                    "2024-01-01 09:01",
                    "2024-01-01 09:02",
                    "2024-01-01 09:03",
                    "2024-01-01 09:04",
                    "2024-01-01 09:05",
                ]
            ),
        ),
        "expected_report": pd.DataFrame(
            {
                "Status": ["OK", "M1_PARTIAL"],
            },
            index=pd.to_datetime(["2024-01-01 09:05", "2024-01-01 09:10"]),
        ),
    },
    {
        "name": "2. All candles present, one m1 candle OHLC mismatch",
        "m5": pd.DataFrame(
            {
                "Open": [100, 105],
                "High": [110, 115],
                "Low": [90, 95],
                "Close": [105, 110],
                "Volume": [500, 600],
            },
            index=pd.to_datetime(["2024-01-01 09:05", "2024-01-01 09:10"]),
        ),
        "m1": pd.DataFrame(
            {
                "Open": [100, 102, 104, 106, 105, 105, 107, 109, 111, 110],
                "High": [102, 104, 106, 110, 107, 107, 109, 111, 116, 112],
                "Low": [99, 90, 103, 105, 104, 104, 95, 108, 110, 109],
                "Close": [102, 104, 106, 107, 105, 109, 111, 110, 112, 110],
                "Volume": [100, 100, 100, 100, 100, 120, 120, 120, 120, 120],
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
        "tol": Tolerances(
            eps_price=1e-5,
            eps_vol=1e-5,
        ),
        "expected_m5": pd.DataFrame(
            {
                "Open": [100],
                "High": [110],
                "Low": [90],
                "Close": [105],
                "Volume": [500],
            },
            index=pd.to_datetime(["2024-01-01 09:05"]),
        ),
        "expected_m1": pd.DataFrame(
            {
                "Open": [100, 102, 104, 106, 105],
                "High": [102, 104, 106, 110, 107],
                "Low": [99, 90, 103, 105, 104],
                "Close": [102, 104, 106, 107, 105],
                "Volume": [100, 100, 100, 100, 100],
            },
            index=pd.to_datetime(
                [
                    "2024-01-01 09:01",
                    "2024-01-01 09:02",
                    "2024-01-01 09:03",
                    "2024-01-01 09:04",
                    "2024-01-01 09:05",
                ]
            ),
        ),
        "expected_report": pd.DataFrame(
            {
                "Status": ["OK", "MISMATCH_OHLC"],
            },
            index=pd.to_datetime(["2024-01-01 09:05", "2024-01-01 09:10"]),
        ),
    },
    {
        "name": "3. All candles present, one m1 candle volume mismatch",
        "m5": pd.DataFrame(
            {
                "Open": [100, 105],
                "High": [110, 115],
                "Low": [90, 95],
                "Close": [105, 110],
                "Volume": [500, 600],
            },
            index=pd.to_datetime(["2024-01-01 09:05", "2024-01-01 09:10"]),
        ),
        "m1": pd.DataFrame(
            {
                "Open": [100, 102, 104, 106, 105, 105, 107, 109, 111, 110],
                "High": [102, 104, 106, 110, 107, 107, 109, 111, 115, 112],
                "Low": [99, 90, 103, 105, 104, 104, 95, 108, 110, 109],
                "Close": [102, 104, 106, 107, 105, 109, 111, 110, 112, 110],
                "Volume": [100, 100, 100, 100, 100, 120, 120, 120, 120, 121],
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
        "tol": Tolerances(
            eps_price=1e-5,
            eps_vol=1e-5,
        ),
        "expected_m5": pd.DataFrame(
            {
                "Open": [100],
                "High": [110],
                "Low": [90],
                "Close": [105],
                "Volume": [500],
            },
            index=pd.to_datetime(["2024-01-01 09:05"]),
        ),
        "expected_m1": pd.DataFrame(
            {
                "Open": [100, 102, 104, 106, 105],
                "High": [102, 104, 106, 110, 107],
                "Low": [99, 90, 103, 105, 104],
                "Close": [102, 104, 106, 107, 105],
                "Volume": [100, 100, 100, 100, 100],
            },
            index=pd.to_datetime(
                [
                    "2024-01-01 09:01",
                    "2024-01-01 09:02",
                    "2024-01-01 09:03",
                    "2024-01-01 09:04",
                    "2024-01-01 09:05",
                ]
            ),
        ),
        "expected_report": pd.DataFrame(
            {
                "Status": ["OK", "MISMATCH_VOLUME"],
            },
            index=pd.to_datetime(["2024-01-01 09:05", "2024-01-01 09:10"]),
        ),
    },
    {
        "name": "4. M5 candles number greater than m1 candles number",
        "m5": pd.DataFrame(
            {
                "Open": [100, 105, 106],
                "High": [110, 112, 115],
                "Low": [90, 85, 95],
                "Close": [105, 106, 110],
                "Volume": [500, 400, 600],
            },
            index=pd.to_datetime(
                ["2024-01-01 09:05", "2024-01-01 09:10", "2024-01-01 09:15"]
            ),
        ),
        "m1": pd.DataFrame(
            {
                "Open": [100, 102, 104, 106, 105, 106, 107, 109, 111, 110],
                "High": [102, 104, 106, 110, 107, 107, 109, 111, 115, 112],
                "Low": [99, 90, 103, 105, 104, 104, 95, 108, 110, 109],
                "Close": [102, 104, 106, 107, 105, 109, 111, 110, 112, 110],
                "Volume": [100, 100, 100, 100, 100, 120, 120, 120, 120, 120],
            },
            index=pd.to_datetime(
                [
                    "2024-01-01 09:01",
                    "2024-01-01 09:02",
                    "2024-01-01 09:03",
                    "2024-01-01 09:04",
                    "2024-01-01 09:05",
                    "2024-01-01 09:11",
                    "2024-01-01 09:12",
                    "2024-01-01 09:13",
                    "2024-01-01 09:14",
                    "2024-01-01 09:15",
                ]
            ),
        ),
        "tol": Tolerances(
            eps_price=1e-5,
            eps_vol=1e-5,
        ),
        "expected_m5": pd.DataFrame(
            {
                "Open": [100, 106],
                "High": [110, 115],
                "Low": [90, 95],
                "Close": [105, 110],
                "Volume": [500, 600],
            },
            index=pd.to_datetime(["2024-01-01 09:05", "2024-01-01 09:15"]),
        ),
        "expected_m1": pd.DataFrame(
            {
                "Open": [100, 102, 104, 106, 105, 106, 107, 109, 111, 110],
                "High": [102, 104, 106, 110, 107, 107, 109, 111, 115, 112],
                "Low": [99, 90, 103, 105, 104, 104, 95, 108, 110, 109],
                "Close": [102, 104, 106, 107, 105, 109, 111, 110, 112, 110],
                "Volume": [100, 100, 100, 100, 100, 120, 120, 120, 120, 120],
            },
            index=pd.to_datetime(
                [
                    "2024-01-01 09:01",
                    "2024-01-01 09:02",
                    "2024-01-01 09:03",
                    "2024-01-01 09:04",
                    "2024-01-01 09:05",
                    "2024-01-01 09:11",
                    "2024-01-01 09:12",
                    "2024-01-01 09:13",
                    "2024-01-01 09:14",
                    "2024-01-01 09:15",
                ]
            ),
        ),
        "expected_report": pd.DataFrame(
            {
                "Status": ["OK", "M1_PARTIAL", "OK"],
            },
            index=pd.to_datetime(
                ["2024-01-01 09:05", "2024-01-01 09:10", "2024-01-01 09:15"]
            ),
        ),
    },
    {
        "name": "5. M5 candles number less than m1 candles number",
        "m5": pd.DataFrame(
            {
                "Open": [100, 105],
                "High": [110, 115],
                "Low": [90, 95],
                "Close": [105, 110],
                "Volume": [500, 600],
            },
            index=pd.to_datetime(["2024-01-01 09:05", "2024-01-01 09:15"]),
        ),
        "m1": pd.DataFrame(
            {
                "Open": [
                    100,
                    102,
                    104,
                    106,
                    105,
                    105,
                    107,
                    109,
                    111,
                    110,
                    105,
                    107,
                    109,
                    111,
                    110,
                ],
                "High": [
                    102,
                    104,
                    106,
                    110,
                    107,
                    107,
                    109,
                    111,
                    115,
                    112,
                    107,
                    109,
                    111,
                    115,
                    112,
                ],
                "Low": [
                    99,
                    90,
                    103,
                    105,
                    104,
                    104,
                    95,
                    108,
                    110,
                    109,
                    104,
                    95,
                    108,
                    110,
                    109,
                ],
                "Close": [
                    102,
                    104,
                    106,
                    107,
                    105,
                    109,
                    111,
                    110,
                    112,
                    110,
                    109,
                    111,
                    110,
                    112,
                    110,
                ],
                "Volume": [
                    100,
                    100,
                    100,
                    100,
                    100,
                    120,
                    120,
                    120,
                    120,
                    120,
                    120,
                    120,
                    120,
                    120,
                    120,
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
                    "2024-01-01 09:11",
                    "2024-01-01 09:12",
                    "2024-01-01 09:13",
                    "2024-01-01 09:14",
                    "2024-01-01 09:15",
                ]
            ),
        ),
        "tol": Tolerances(
            eps_price=1e-5,
            eps_vol=1e-5,
        ),
        "expected_m5": pd.DataFrame(
            {
                "Open": [100, 105],
                "High": [110, 115],
                "Low": [90, 95],
                "Close": [105, 110],
                "Volume": [500, 600],
            },
            index=pd.to_datetime(["2024-01-01 09:05", "2024-01-01 09:15"]),
        ),
        "expected_m1": pd.DataFrame(
            {
                "Open": [100, 102, 104, 106, 105, 105, 107, 109, 111, 110],
                "High": [102, 104, 106, 110, 107, 107, 109, 111, 115, 112],
                "Low": [99, 90, 103, 105, 104, 104, 95, 108, 110, 109],
                "Close": [102, 104, 106, 107, 105, 109, 111, 110, 112, 110],
                "Volume": [100, 100, 100, 100, 100, 120, 120, 120, 120, 120],
            },
            index=pd.to_datetime(
                [
                    "2024-01-01 09:01",
                    "2024-01-01 09:02",
                    "2024-01-01 09:03",
                    "2024-01-01 09:04",
                    "2024-01-01 09:05",
                    "2024-01-01 09:11",
                    "2024-01-01 09:12",
                    "2024-01-01 09:13",
                    "2024-01-01 09:14",
                    "2024-01-01 09:15",
                ]
            ),
        ),
        "expected_report": pd.DataFrame(
            {
                "Status": ["OK", "OK"],
            },
            index=pd.to_datetime(["2024-01-01 09:05", "2024-01-01 09:15"]),
        ),
    },
    {
        "name": "6. All candles present, OHLC diff exactly eps -> OK",
        "m5": pd.DataFrame(
            {
                "Open": [100],
                "High": [110],
                "Low": [90],
                "Close": [105],
                "Volume": [500],
            },
            index=pd.to_datetime(["2024-01-01 09:05"]),
        ),
        "m1": pd.DataFrame(
            {
                "Open": [100, 102, 104, 106, 105],
                "High": [102, 104, 106, 110, 107.00001],  # +1e-5 к high окна
                "Low": [99, 90, 103, 105, 104],
                "Close": [102, 104, 106, 107, 105],
                "Volume": [100, 100, 100, 100, 100],
            },
            index=pd.to_datetime(
                [
                    "2024-01-01 09:01",
                    "2024-01-01 09:02",
                    "2024-01-01 09:03",
                    "2024-01-01 09:04",
                    "2024-01-01 09:05",
                ]
            ),
        ),
        "tol": Tolerances(eps_price=1e-5, eps_vol=1e-5),
        "expected_m5": pd.DataFrame(
            {
                "Open": [100],
                "High": [110],
                "Low": [90],
                "Close": [105],
                "Volume": [500],
            },
            index=pd.to_datetime(["2024-01-01 09:05"]),
        ),
        "expected_m1": pd.DataFrame(
            {
                "Open": [100, 102, 104, 106, 105],
                "High": [102, 104, 106, 110, 107.00001],
                "Low": [99, 90, 103, 105, 104],
                "Close": [102, 104, 106, 107, 105],
                "Volume": [100, 100, 100, 100, 100],
            },
            index=pd.to_datetime(
                [
                    "2024-01-01 09:01",
                    "2024-01-01 09:02",
                    "2024-01-01 09:03",
                    "2024-01-01 09:04",
                    "2024-01-01 09:05",
                ]
            ),
        ),
        "expected_report": pd.DataFrame(
            {"Status": ["OK"]},
            index=pd.to_datetime(["2024-01-01 09:05"]),
        ),
    },
    {
        "name": "7. All candles present, OHLC diff > eps -> MISMATCH_OHLC",
        "m5": pd.DataFrame(
            {
                "Open": [100],
                "High": [110],
                "Low": [90],
                "Close": [105],
                "Volume": [500],
            },
            index=pd.to_datetime(["2024-01-01 09:05"]),
        ),
        "m1": pd.DataFrame(
            {
                "Open": [100, 102, 104, 106, 105],
                "High": [102, 104, 106, 110.00002, 107],  # +1.00002e-5 > eps
                "Low": [99, 90, 103, 105, 104],
                "Close": [102, 104, 106, 107, 105],
                "Volume": [100, 100, 100, 100, 100],
            },
            index=pd.to_datetime(
                [
                    "2024-01-01 09:01",
                    "2024-01-01 09:02",
                    "2024-01-01 09:03",
                    "2024-01-01 09:04",
                    "2024-01-01 09:05",
                ]
            ),
        ),
        "tol": Tolerances(eps_price=1e-5, eps_vol=1e-5),
        "expected_m5": pd.DataFrame(
            {
                "Open": pd.Series(dtype="int64"),
                "High": pd.Series(dtype="int64"),
                "Low": pd.Series(dtype="int64"),
                "Close": pd.Series(dtype="int64"),
                "Volume": pd.Series(dtype="int64"),
            },
            index=pd.to_datetime([]),
        ),
        "expected_m1": pd.DataFrame(
            {
                "Open": pd.Series(dtype="int64"),
                "High": pd.Series(dtype="float64"),  # из-за 110.00002
                "Low": pd.Series(dtype="int64"),
                "Close": pd.Series(dtype="int64"),
                "Volume": pd.Series(dtype="int64"),
            },
            index=pd.to_datetime([]),
        ),
        "expected_report": pd.DataFrame(
            {"Status": ["MISMATCH_OHLC"]},
            index=pd.to_datetime(["2024-01-01 09:05"]),
        ),
    },
    {
        "name": "8. All candles present, volume diff exactly eps -> OK",
        "m5": pd.DataFrame(
            {
                "Open": [100],
                "High": [110],
                "Low": [90],
                "Close": [105],
                "Volume": [500],
            },
            index=pd.to_datetime(["2024-01-01 09:05"]),
        ),
        "m1": pd.DataFrame(
            {
                "Open": [100, 102, 104, 106, 105],
                "High": [102, 104, 106, 110, 107],
                "Low": [99, 90, 103, 105, 104],
                "Close": [102, 104, 106, 107, 105],
                "Volume": [100, 100, 100, 100, 100.00001],  # +1e-5 к объёму
            },
            index=pd.to_datetime(
                [
                    "2024-01-01 09:01",
                    "2024-01-01 09:02",
                    "2024-01-01 09:03",
                    "2024-01-01 09:04",
                    "2024-01-01 09:05",
                ]
            ),
        ),
        "tol": Tolerances(eps_price=1e-5, eps_vol=1e-5),
        "expected_m5": pd.DataFrame(
            {
                "Open": [100],
                "High": [110],
                "Low": [90],
                "Close": [105],
                "Volume": [500],
            },
            index=pd.to_datetime(["2024-01-01 09:05"]),
        ),
        "expected_m1": pd.DataFrame(
            {
                "Open": [100, 102, 104, 106, 105],
                "High": [102, 104, 106, 110, 107],
                "Low": [99, 90, 103, 105, 104],
                "Close": [102, 104, 106, 107, 105],
                "Volume": [100, 100, 100, 100, 100.00001],
            },
            index=pd.to_datetime(
                [
                    "2024-01-01 09:01",
                    "2024-01-01 09:02",
                    "2024-01-01 09:03",
                    "2024-01-01 09:04",
                    "2024-01-01 09:05",
                ]
            ),
        ),
        "expected_report": pd.DataFrame(
            {"Status": ["OK"]},
            index=pd.to_datetime(["2024-01-01 09:05"]),
        ),
    },
    {
        "name": "9. All candles present, volume diff > eps -> MISMATCH_VOLUME",
        "m5": pd.DataFrame(
            {
                "Open": [100],
                "High": [110],
                "Low": [90],
                "Close": [105],
                "Volume": [500],
            },
            index=pd.to_datetime(["2024-01-01 09:05"]),
        ),
        "m1": pd.DataFrame(
            {
                "Open": [100, 102, 104, 106, 105],
                "High": [102, 104, 106, 110, 107],
                "Low": [99, 90, 103, 105, 104],
                "Close": [102, 104, 106, 107, 105],
                "Volume": [100, 100, 100, 100, 100.00002],  # > eps
            },
            index=pd.to_datetime(
                [
                    "2024-01-01 09:01",
                    "2024-01-01 09:02",
                    "2024-01-01 09:03",
                    "2024-01-01 09:04",
                    "2024-01-01 09:05",
                ]
            ),
        ),
        "tol": Tolerances(eps_price=1e-5, eps_vol=1e-5),
        "expected_m5": pd.DataFrame(
            {
                "Open": pd.Series(dtype="int64"),
                "High": pd.Series(dtype="int64"),
                "Low": pd.Series(dtype="int64"),
                "Close": pd.Series(dtype="int64"),
                "Volume": pd.Series(dtype="int64"),
            },
            index=pd.to_datetime([]),
        ),
        "expected_m1": pd.DataFrame(
            {
                "Open": pd.Series(dtype="int64"),
                "High": pd.Series(dtype="int64"),
                "Low": pd.Series(dtype="int64"),
                "Close": pd.Series(dtype="int64"),
                "Volume": pd.Series(dtype="float64"),
            },
            index=pd.to_datetime([]),
        ),
        "expected_report": pd.DataFrame(
            {"Status": ["MISMATCH_VOLUME"]},
            index=pd.to_datetime(["2024-01-01 09:05"]),
        ),
    },
    {
        "name": "10. All candles present, NaN in m1 OHLC -> OK",
        "m5": pd.DataFrame(
            {
                "Open": [100],
                "High": [110],
                "Low": [90],
                "Close": [105],
                "Volume": [500],
            },
            index=pd.to_datetime(["2024-01-01 09:05"]),
        ),
        "m1": pd.DataFrame(
            {
                "Open": [100, 102, 104, 106, 105],
                "High": [102, 104, float("nan"), 110, 107],  # NaN ломает high окна
                "Low": [99, 90, 103, 105, 104],
                "Close": [102, 104, 106, 107, 105],
                "Volume": [100, 100, 100, 100, 100],
            },
            index=pd.to_datetime(
                [
                    "2024-01-01 09:01",
                    "2024-01-01 09:02",
                    "2024-01-01 09:03",
                    "2024-01-01 09:04",
                    "2024-01-01 09:05",
                ]
            ),
        ),
        "tol": Tolerances(eps_price=1e-5, eps_vol=1e-5),
        "expected_m5": pd.DataFrame(
            {
                "Open": [100],
                "High": [110],
                "Low": [90],
                "Close": [105],
                "Volume": [500],
            },
            index=pd.to_datetime(["2024-01-01 09:05"]),
        ),
        "expected_m1": pd.DataFrame(
            {
                "Open": [100, 102, 104, 106, 105],
                "High": [102, 104, float("nan"), 110, 107],
                "Low": [99, 90, 103, 105, 104],
                "Close": [102, 104, 106, 107, 105],
                "Volume": [100, 100, 100, 100, 100],
            },
            index=pd.to_datetime(
                [
                    "2024-01-01 09:01",
                    "2024-01-01 09:02",
                    "2024-01-01 09:03",
                    "2024-01-01 09:04",
                    "2024-01-01 09:05",
                ]
            ),
        ),
        "expected_report": pd.DataFrame(
            {"Status": ["OK"]},
            index=pd.to_datetime(["2024-01-01 09:05"]),
        ),
    },
    {
        "name": "11. All candles present, m1 columns reordered -> OK",
        "m5": pd.DataFrame(
            {
                "Open": [100],
                "High": [110],
                "Low": [90],
                "Close": [105],
                "Volume": [500],
            },
            index=pd.to_datetime(["2024-01-01 09:05"]),
        ),
        # порядок колонок: Close, Low, Volume, High, Open
        "m1": pd.DataFrame(
            {
                "Close": [102, 104, 106, 107, 105],
                "Low": [99, 90, 103, 105, 104],
                "Volume": [100, 100, 100, 100, 100],
                "High": [102, 104, 106, 110, 107],
                "Open": [100, 102, 104, 106, 105],
            },
            index=pd.to_datetime(
                [
                    "2024-01-01 09:01",
                    "2024-01-01 09:02",
                    "2024-01-01 09:03",
                    "2024-01-01 09:04",
                    "2024-01-01 09:05",
                ]
            ),
        ),
        "tol": Tolerances(eps_price=1e-5, eps_vol=1e-5),
        "expected_m5": pd.DataFrame(
            {
                "Open": [100],
                "High": [110],
                "Low": [90],
                "Close": [105],
                "Volume": [500],
            },
            index=pd.to_datetime(["2024-01-01 09:05"]),
        ),
        "expected_m1": pd.DataFrame(
            {
                "Close": [102, 104, 106, 107, 105],
                "Low": [99, 90, 103, 105, 104],
                "Volume": [100, 100, 100, 100, 100],
                "High": [102, 104, 106, 110, 107],
                "Open": [100, 102, 104, 106, 105],
            },
            index=pd.to_datetime(
                [
                    "2024-01-01 09:01",
                    "2024-01-01 09:02",
                    "2024-01-01 09:03",
                    "2024-01-01 09:04",
                    "2024-01-01 09:05",
                ]
            ),
        ),
        "expected_report": pd.DataFrame(
            {"Status": ["OK"]},
            index=pd.to_datetime(["2024-01-01 09:05"]),
        ),
    },
]


@pytest.mark.parametrize(
    "case", sync_test_cases, ids=[c["name"] for c in sync_test_cases]
)
def test_sync_m5_m1(case):
    aligned_m5, aligned_m1, report = sync_m5_m1(case["m5"], case["m1"], case["tol"])

    pd.testing.assert_frame_equal(aligned_m5, case["expected_m5"])
    pd.testing.assert_frame_equal(aligned_m1, case["expected_m1"])
    pd.testing.assert_frame_equal(report, case["expected_report"])
