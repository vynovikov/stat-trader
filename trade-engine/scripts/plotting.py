import os
import sys

# Получаем путь к текущему скрипту
current_dir = os.path.dirname(os.path.abspath(__file__))

# Поднимаемся на два уровня выше, чтобы попасть в корневой каталог проекта (ml-agent)
# Путь может быть другим, в зависимости от того, где находится config.py
project_root = os.path.abspath(os.path.join(current_dir, ".."))

# Добавляем корневой каталог в sys.path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from datetime import datetime, timedelta

import mplfinance as mpf
import pandas as pd

from domain.types.candle import Candle


def expand_candles(
    df: pd.DataFrame, gap: timedelta = timedelta(minutes=2.5)
) -> pd.DataFrame:
    """Добавляет пустые временные промежутки между свечами, чтобы график выглядел разреженным."""
    expanded = []
    for i in range(len(df) - 1):
        expanded.append(df.iloc[i])
        expanded.append(pd.Series(dtype="float64", name=df.index[i] + gap))
    expanded.append(df.iloc[-1])
    return pd.DataFrame(expanded)


if __name__ == "__main__":
    # --- данные ---
    candles = [
        Candle(
            high=100.5,
            low=100.4,
            open=100.45,
            close=100.48,
            close_time=datetime(2025, 1, 1, 0, 0),
            volume=1000,
        ),
        Candle(
            high=100.4,
            low=100.3,
            open=100.55,
            close=100.58,
            close_time=datetime(2025, 1, 1, 0, 5),
            volume=1001,
        ),
        Candle(
            high=100.6,
            low=100.2,
            open=100.45,
            close=100.48,
            close_time=datetime(2025, 1, 1, 0, 10),
            volume=1002,
        ),
        Candle(
            high=100.6,
            low=100.5,
            open=100.55,
            close=100.58,
            close_time=datetime(2025, 1, 1, 0, 15),
            volume=1003,
        ),
        Candle(
            high=100.5,
            low=100.4,
            open=100.45,
            close=100.48,
            close_time=datetime(2025, 1, 1, 0, 20),
            volume=1004,
        ),
        Candle(
            high=100.4,
            low=100.3,
            open=100.55,
            close=100.58,
            close_time=datetime(2025, 1, 1, 0, 25),
            volume=1005,
        ),
        Candle(
            high=100.7,
            low=100.6,
            open=100.45,
            close=100.48,
            close_time=datetime(2025, 1, 1, 0, 30),
            volume=1006,
        ),
        Candle(
            high=100.6,
            low=100.5,
            open=100.55,
            close=100.58,
            close_time=datetime(2025, 1, 1, 0, 35),
            volume=1007,
        ),
        Candle(
            high=100.7,
            low=100.4,
            open=100.58,
            close=100.48,
            close_time=datetime(2025, 1, 1, 0, 40),
            volume=1008,
        ),
        Candle(
            high=100.5,
            low=100.3,
            open=100.48,
            close=100.38,
            close_time=datetime(2025, 1, 1, 0, 45),
            volume=1009,
        ),
        Candle(
            high=100.4,
            low=100.2,
            open=100.38,
            close=100.28,
            close_time=datetime(2025, 1, 1, 0, 50),
            volume=1010,
        ),
        Candle(
            high=100.4,
            low=100.1,
            open=100.28,
            close=100.18,
            close_time=datetime(2025, 1, 1, 0, 55),
            volume=1011,
        ),
    ]

    raw = [c._asdict() for c in candles]
    df = pd.DataFrame(raw)
    mpl_df = df.rename(
        columns={
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume",
        }
    ).set_index(pd.to_datetime(df["close_time"]))[
        ["Open", "High", "Low", "Close", "Volume"]
    ]
    mpl_df = expand_candles(df=mpl_df, gap=timedelta(minutes=2.5))

    price = candles[2].open
    thin_left = candles[2].close_time + timedelta(minutes=1)
    thin_right = candles[2].close_time + timedelta(minutes=5)

    lines = [
        [(thin_left, price), (thin_right, price)],
    ]

    mpf.plot(
        mpl_df,
        type="candle",
        style="charles",
        volume=True,
        alines=dict(
            alines=lines,
            colors="r",
            linestyle="-",
            linewidths=2,
            alpha=0.8,
        ),
        title="Sample Candlestick Chart",
        ylabel="Price",
        ylabel_lower="Volume",
        savefig="data/candles/BTCUSDT/trend/1.png",
    )
