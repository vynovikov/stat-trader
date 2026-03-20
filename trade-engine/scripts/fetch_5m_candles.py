#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
from binance.spot import Spot

# Binance отдаёт максимум 1000 свечей за запрос
MAX_LIMIT = 1000
INTERVAL = "5m"
INTERVAL_MS = 5 * 60 * 1000


def to_ms(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


def main():
    ap = argparse.ArgumentParser(
        description="Fetch Binance Spot 5m candles for the last N months."
    )
    ap.add_argument(
        "--symbol", default="BTCUSDT", help="Торговая пара (по умолчанию BTCUSDT)"
    )
    ap.add_argument(
        "--months", type=int, default=2, help="Сколько месяцев назад (по умолчанию 2)"
    )
    ap.add_argument(
        "--skip-last-minutes",
        type=int,
        default=5,
        help="Сколько минут с конца пропустить, чтобы не ловить незакрытую свечу (по умолчанию 5)",
    )
    ap.add_argument(
        "--out",
        default="candles_5m.csv",
        help="Путь к файлу CSV (по умолчанию candles_5m.csv)",
    )
    args = ap.parse_args()

    client = Spot()  # публичные эндпоинты, ключ не нужен

    # Временной диапазон: последние N месяцев до "сейчас - skip_last"
    end_utc = datetime.now(timezone.utc) - timedelta(minutes=args.skip_last_minutes)
    start_utc = end_utc - timedelta(days=30 * args.months)

    start_ms = to_ms(start_utc)
    end_ms = to_ms(end_utc)

    all_rows: list[list] = []
    symbol = args.symbol.upper()

    print(
        f"Downloading {symbol} {INTERVAL} from {start_utc.isoformat()} to {end_utc.isoformat()} ..."
    )

    while True:
        batch = client.klines(
            symbol=symbol, interval=INTERVAL, startTime=start_ms, limit=MAX_LIMIT
        )

        if not batch:
            break

        all_rows.extend(batch)

        last_open = batch[-1][0]
        # если дошли до конца диапазона — выходим
        if last_open + INTERVAL_MS >= end_ms:
            break

        # следующая страница: с миллисекунды после последней открытой свечи
        start_ms = last_open + 1

        # бережная пауза, чтобы не упереться в rate limit (обычно необязательно, но полезно)
        time.sleep(0.05)

    print(f"Downloaded candles: {len(all_rows)}")

    # В DataFrame + приведение временных меток
    df = pd.DataFrame(
        all_rows,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_volume",
            "trades",
            "taker_base",
            "taker_quote",
            "ignore",
        ],
    )
    if df.empty:
        print("No data received. Check symbol or timeframe range.")
        return

    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms", utc=True)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Saved to {out_path.resolve()}")


if __name__ == "__main__":
    main()
