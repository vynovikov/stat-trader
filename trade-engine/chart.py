from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import requests

# Запрашиваем данные
url = "https://api.binance.com/api/v3/klines"
params = {"symbol": "BTCUSDT", "interval": "1m", "limit": 1440}
response = requests.get(url, params=params)
data = response.json()

if isinstance(data, dict):
    print("Ошибка от Binance:", data)
    exit()

# Преобразуем в DataFrame
df = pd.DataFrame(
    data,
    columns=[
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_asset_volume",
        "number_of_trades",
        "taker_buy_base",
        "taker_buy_quote",
        "ignore",
    ],
)
df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
df["close"] = df["close"].astype(float)

print(f"Статус: {response.status_code}, длина данных: {len(data)}")
print(data[:3])  # покажет первые 3 записи

print(df["close"].head())
print(df.dtypes)


# Строим график
plt.figure(figsize=(14, 6))
plt.plot(df["open_time"], df["close"])
plt.title("BTC/USDT — Цена закрытия (1m интервал)")
plt.xlabel("Время")
plt.ylabel("Цена (USDT)")
plt.grid(True)
plt.tight_layout()
plt.savefig("chart.png")
print("График сохранён в chart.png")
