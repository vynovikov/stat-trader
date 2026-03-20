from dataclasses import dataclass
from typing import Tuple

import pandas as pd


@dataclass
class Tolerances:
    eps_price: float = 1e-8
    eps_vol: float = 1e-8


def _norm_index(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("Index must be DatetimeIndex (close times).")

    return df.sort_index()


def eq(a: float, b: float, eps: float) -> bool:

    return abs(float(a) - float(b)) <= eps


def sync_m5_m1(
    m5: pd.DataFrame, m1: pd.DataFrame, tol: Tolerances = Tolerances()
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Синхронизирует 5-минутные и 1-минутные свечи.
    Возвращает:
      - aligned_m5: только те m5-свечи, у которых найдено точное окно из 5×m1
      - aligned_m1: конкатенация всех найденных m1-окон
      - report: статус для каждой m5-свечи
    """

    m5 = _norm_index(m5)
    m1 = _norm_index(m1)

    aligned_m5_rows: list[pd.Series] = []
    aligned_m1_parts: list[pd.DataFrame] = []
    report_rows: list[tuple[pd.Timestamp, str]] = []

    m1_times = m1.index
    i = 0

    for T in m5.index:
        start = T - pd.Timedelta(minutes=4)

        while i < len(m1_times) and m1_times[i] < start:
            i += 1

        needed = [start + pd.Timedelta(minutes=k) for k in range(5)]
        window_rows = []
        j = i

        for t in needed:
            if j < len(m1_times) and m1_times[j] == t:
                window_rows.append(m1.iloc[j])
                j += 1
            else:
                report_rows.append((T, "M1_PARTIAL"))
                window_rows = []
                break

        if not window_rows:
            continue

        m1_block = m1.iloc[i:j].copy()

        o = float(m1_block["Open"].iloc[0])
        h = float(m1_block["High"].max())
        l = float(m1_block["Low"].min())
        c = float(m1_block["Close"].iloc[-1])
        v = float(m1_block["Volume"].sum())

        m5_row = m5.loc[T]

        agg_ok = (
            eq(m5_row["Open"], o, tol.eps_price)
            and eq(m5_row["High"], h, tol.eps_price)
            and eq(m5_row["Low"], l, tol.eps_price)
            and eq(m5_row["Close"], c, tol.eps_price)
        )
        vol_ok = eq(m5_row["Volume"], v, tol.eps_vol)

        if agg_ok and vol_ok:
            aligned_m5_rows.append(m5_row.rename(T))
            aligned_m1_parts.append(m1_block)
            report_rows.append((T, "OK"))
            i = j
        else:
            report_rows.append((T, "MISMATCH_VOLUME" if agg_ok else "MISMATCH_OHLC"))

    aligned_m5 = (
        pd.DataFrame(aligned_m5_rows, index=[r.name for r in aligned_m5_rows])
        if aligned_m5_rows
        else m5.iloc[0:0]
    )
    aligned_m1 = pd.concat(aligned_m1_parts) if aligned_m1_parts else m1.iloc[0:0]
    report = (
        pd.DataFrame(report_rows, columns=["close_time", "Status"])
        .set_index("close_time")
        .reindex(m5.index, fill_value="M1_MISSING")
    )

    return aligned_m5, aligned_m1, report
