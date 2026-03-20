"""
Utility functions for candle data processing.
"""

from datetime import date, datetime, timedelta, timezone
from typing import Any, List

import numpy as np
import pandas as pd

from domain.types.candle import Candle


def calculate_avg_candle_length(df: pd.DataFrame) -> float:
    """
    Calculate the average candle length from a DataFrame of candle data.

    Args:
        df: DataFrame with columns ['open', 'high', 'low', 'close']

    Returns:
        Average full length of candles (body + upper shadow + lower shadow)
    """
    if df.empty:
        return 0.0

    temp_df = df.copy()

    # Calculate body length
    temp_df["body_length"] = abs(temp_df["close"] - temp_df["open"])

    # Calculate upper shadow
    temp_df["upper_shadow"] = temp_df["high"] - temp_df[["close", "open"]].max(axis=1)

    # Calculate lower shadow
    temp_df["lower_shadow"] = temp_df[["close", "open"]].min(axis=1) - temp_df["low"]

    # Calculate full length
    temp_df["full_length"] = (
        temp_df["upper_shadow"] + temp_df["body_length"] + temp_df["lower_shadow"]
    )

    return temp_df["full_length"].mean()


def get_candles(df: pd.DataFrame) -> List[Candle]:
    """
    Convert a DataFrame of candle data into a list of Candle objects.

    Args:
        df: DataFrame with columns ['open', 'high', 'low', 'close', 'volume', 'ma_50', 'ma_200']

    Returns:
        List of Candle objects
    """
    candles: List[Candle] = []
    for row in df.itertuples(index=False):
        close_time_dt = _parse_close_time(getattr(row, "close_time"))

        candle = Candle(
            open=getattr(row, "open"),
            high=getattr(row, "high"),
            low=getattr(row, "low"),
            close=getattr(row, "close"),
            volume=getattr(row, "volume"),
            # ma_50=getattr(row, "ma_50"),
            # ma_200=getattr(row, "ma_200"),
            close_time=close_time_dt,
        )
        candles.append(candle)

    return candles


def candle_from_series(series: pd.Series) -> Candle:
    """
    Build Candle from a pandas Series.
    - Источник времени: 'Close time' если есть, иначе индекс серии.
    - Поддерживает строки с миллисекундами/микросекундами и без них, а также datetime/np.datetime64/pd.Timestamp.
    - Округляет до ближайшей секунды.
    - Если Timestamp с таймзоной — делает его naive (убирает tz).
    """

    o = float(series["open"])
    h = float(series["high"])
    l = float(series["low"])
    c = float(series["close"])
    v = float(series["volume"])

    raw_time: Any = (
        series["close time"] if "close time" in series.index else series.name
    )
    if raw_time is None:
        raise ValueError(
            "close time is missing: neither 'close time' column nor index provided"
        )

    ts = pd.Timestamp(raw_time)
    if ts.tz is not None:
        ts = ts.tz_convert(None).tz_localize(None)
    ts = ts.round("s")

    return Candle(open=o, high=h, low=l, close=c, volume=v, close_time=ts)


def _parse_close_time(val) -> datetime:
    """Парсит разные варианты времени и приводит к UTC-naive + округление half-up."""
    # 1) Преобразуем к datetime
    if isinstance(val, pd.Timestamp):
        dt = val.to_pydatetime()
    elif isinstance(val, datetime):
        dt = val
    else:
        s = str(val)
        # поддержим 'Z'
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        try:
            dt = datetime.fromisoformat(s)  # понимает '+HH:MM'
        except ValueError:
            # резервный вариант для строк без TZ
            dt = datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f")

    # 2) Нормализуем TZ: делаем UTC-naive (если нужна tz-aware — закомментируй следующий блок)
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)

    # 3) Округление до секунды half-up
    #    (>= 500_000 мкс → +1 сек, иначе просто обнуляем микросекунды)
    if dt.microsecond >= 500_000:
        dt = dt.replace(microsecond=0) + timedelta(seconds=1)
    else:
        dt = dt.replace(microsecond=0)

    return dt
