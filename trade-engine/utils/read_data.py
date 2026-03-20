"""
Utility functions for candle data processing.
"""

import pandas as pd


def read_data(
    input_file: str, offset_hours: int = 10, limit_hours: int = 1
) -> pd.DataFrame:
    """
    Читает данные из CSV файла с 5-минутными свечами.
    Args:
        input_file: путь к файлу с данными
        offset_hours: смещение в часах от начала файла
        limit_hours: количество часов данных для чтения
    Returns:
        DataFrame с данными за указанный период
    """
    df = pd.read_csv(input_file)
    df.columns = df.columns.str.lower()
    # В 1 часе = 12 свечей по 5 минут
    CANDLES_PER_HOUR = 12
    offset_rows = CANDLES_PER_HOUR * offset_hours
    limit_rows = CANDLES_PER_HOUR * limit_hours

    return df.iloc[offset_rows : offset_rows + limit_rows]


def read_all_data(input_file: str) -> pd.DataFrame:
    """
    Читает данные из CSV файла с 5-минутными свечами.
    Args:
        input_file: путь к файлу с данными
    Returns:
        DataFrame с данными за указанный период
    """

    return pd.read_csv(input_file)
