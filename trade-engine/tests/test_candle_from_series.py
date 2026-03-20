from typing import Dict

import numpy as np
import pandas as pd
import pytest

from domain.types.candle import Candle
from utils.candle_utils import candle_from_series


def _mk_series(close_time_present=True, close_time_value=None, name=None):
    """
    Build a Series representing a candle.
    - If close_time_present is False -> no 'Close time' key (index will be used).
    - 'name' sets the Series index label (used as fallback time source).
    """
    payload: Dict[str, object] = {
        "Open": 100,
        "High": 110,
        "Low": 90,
        "Close": 105,
        "Volume": 500,
    }
    if close_time_present:
        payload["Close time"] = close_time_value
    s = pd.Series(payload)
    if name is not None:
        s.name = name
    return s


candle_from_series_cases = [
    {
        "name": "0. Close time as string with microseconds -> rounds up",
        "series": _mk_series(
            close_time_present=True,
            close_time_value="2024-01-01 01:09:04.990",
        ),
        "expected": Candle(
            open=100.0,
            high=110.0,
            low=90.0,
            close=105.0,
            volume=500.0,
            close_time=pd.Timestamp("2024-01-01 01:09:05"),
        ),
        "expected_error": "",
    },
    {
        "name": "1. Close time as string without fractions -> unchanged",
        "series": _mk_series(
            close_time_present=True,
            close_time_value="2024-01-01 01:09:04",
        ),
        "expected": Candle(
            open=100.0,
            high=110.0,
            low=90.0,
            close=105.0,
            volume=500.0,
            close_time=pd.Timestamp("2024-01-01 01:09:04"),
        ),
        "expected_error": "",
    },
    {
        "name": "2. Close time as string with microseconds -> rounds down",
        "series": _mk_series(
            close_time_present=True,
            close_time_value="2024-01-01 01:09:04.049",
        ),
        "expected": Candle(
            open=100.0,
            high=110.0,
            low=90.0,
            close=105.0,
            volume=500.0,
            close_time=pd.Timestamp("2024-01-01 01:09:04"),
        ),
        "expected_error": "",
    },
    {
        "name": "3. Close time from index fallback (no column) -> rounds up",
        "series": _mk_series(
            close_time_present=False,
            name=pd.Timestamp("2024-01-01 01:09:04.501"),
        ),
        "expected": Candle(
            open=100.0,
            high=110.0,
            low=90.0,
            close=105.0,
            volume=500.0,
            close_time=pd.Timestamp("2024-01-01 01:09:05"),
        ),
        "expected_error": "",
    },
    {
        "name": "4. Close time as numpy.datetime64 -> rounds down",
        "series": _mk_series(
            close_time_present=True,
            close_time_value=np.datetime64("2024-01-01T01:09:04.499000"),
        ),
        "expected": Candle(
            open=100.0,
            high=110.0,
            low=90.0,
            close=105.0,
            volume=500.0,
            close_time=pd.Timestamp("2024-01-01 01:09:04"),
        ),
        "expected_error": "",
    },
    {
        "name": "5. Close time as tz-aware Timestamp -> tz dropped, rounds up",
        "series": _mk_series(
            close_time_present=True,
            close_time_value=pd.Timestamp("2024-01-01 01:09:04.600", tz="UTC"),
        ),
        "expected": Candle(
            open=100.0,
            high=110.0,
            low=90.0,
            close=105.0,
            volume=500.0,
            close_time=pd.Timestamp("2024-01-01 01:09:05"),
        ),
        "expected_error": "",
    },
    {
        "name": "6. Error when no 'Close time' and index name is None",
        "series": _mk_series(close_time_present=False, name=None),
        "expected": Candle(
            open=0,
            high=0,
            low=0,
            close=0,
            volume=0,
            close_time=pd.Timestamp("1970-01-01"),
        ),
        "expected_error": "Close time is missing",
    },
]


@pytest.mark.parametrize(
    "case", candle_from_series_cases, ids=[c["name"] for c in candle_from_series_cases]
)
def test_candle_from_series(case):
    series = case["series"]

    if case["expected_error"]:
        with pytest.raises(ValueError, match=case["expected_error"]):
            _ = candle_from_series(series)
        return

    candle = candle_from_series(series)

    assert (
        candle == case["expected"]
    ), "Candle fields (including rounded close_time) must match expected"
    # sanity: ensure close_time is naive (no tz)
    assert pd.Timestamp(candle.close_time).tz is None
    assert pd.Timestamp(candle.close_time).tz is None
