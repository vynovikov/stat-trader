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

from typing import List

import pandas as pd

from config.config import QdrantConfig
from domain.models.segment import Segment
from marker.marker import Marker
from services.repository import QdrantRepository
from services.repository.interface import Repository
from utils.read_data import read_data


def get_segments(df: pd.DataFrame) -> List[Segment]:
    marker = Marker(a_len=8)
    segments = marker.mark(df)
    return segments


def dosmthg(repo: Repository):
    base_df = read_data(
        input_file="data/candles/BTCUSDT/ma_added/BTCUSDT_5m_ma.csv",
        offset_hours=0,
        limit_hours=24,
    )

    segments = get_segments(base_df)
    for id, segment in enumerate(segments):
        segment.update_pattern_characteristics()
        repo.upsert(id=id, segment=segment)


if __name__ == "__main__":
    config = QdrantConfig.from_env()
    qdrant_repository = QdrantRepository(symbol="IFACE", config=config)

    dosmthg(qdrant_repository)
