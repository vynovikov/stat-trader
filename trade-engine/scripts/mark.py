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

from config.config import qdrant_config
from marker.marker import Marker
from services.estimator.reversal_estimator import ReversalEstimator
from services.plotter.plotter import Plotter
from services.repository import QdrantRepository
from utils.read_data import read_data


def get_repository(symbol: str) -> QdrantRepository:
    config = qdrant_config
    repository = QdrantRepository(symbol=symbol, config=config)
    return repository


if __name__ == "__main__":
    repository = get_repository(symbol="BTCUSDT")

    repository.clear_collection()

    plotter = Plotter("data/candles/BTCUSDT/output")

    base_df = read_data(
        input_file="data/candles/BTCUSDT/ma_added/BTCUSDT_5m_last_two_months_ma.csv",
        offset_hours=24 * 7 * 0,
        limit_hours=24 * 7 * 2,
    )

    estimator = ReversalEstimator()
    marker = Marker(estimator=estimator, a_len=4)
    segments = marker.mark(base_df)

    plotter = Plotter("data/candles/BTCUSDT/output")

    for id, segment in enumerate(segments):
        segment.update_pattern_characteristics(
            candles_limit=4,
            ma_50s=base_df["ma_50"].tolist(),
            ma_200s=base_df["ma_200"].tolist(),
        )
        repository.upsert(id, segment)
        # plotter.plot_simple(
        #    candles=segment.Trend, folder_name="segments", file_name=str(id)
        # )
