import os
from datetime import datetime, timedelta

import pandas as pd


def prepare_data():
    # Создаем директорию для сырых данных, если её нет
    raw_dir = "data/candles/BTCUSDT/raw"
    os.makedirs(raw_dir, exist_ok=True)

    # Читаем данные с MA
    df = pd.read_csv("data/candles/BTCUSDT/ma_added/BTCUSDT_5m_klines_complete_ma.csv")

    # Конвертируем время в datetime
    df["Open time"] = pd.to_datetime(df["Open time"])

    # Берем первые два дня данных
    start_date = df["Open time"].min()
    end_date = start_date + timedelta(days=2)
    df_subset = df[df["Open time"] <= end_date].copy()

    # Приводим названия колонок к нижнему регистру для совместимости с маркером
    column_mapping = {
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
    }
    df_subset.rename(columns=column_mapping, inplace=True)

    # Сохраняем подмножество данных
    output_file = os.path.join(raw_dir, "1h.csv")
    df_subset.to_csv(output_file, index=False)

    print(f"Данные сохранены в {output_file}")
    print(f"Период: с {df_subset['Open time'].min()} по {df_subset['Open time'].max()}")
    print(f"Количество свечей: {len(df_subset)}")


if __name__ == "__main__":
    prepare_data()
