"""
Qdrant implementation of vector space for trading patterns.
"""

import os
import sys

# Получаем путь к текущему скрипту
current_dir = os.path.dirname(os.path.abspath(__file__))

# Поднимаемся на два уровня выше, чтобы попасть в корневой каталог проекта (ml-agent)
# Путь может быть другим, в зависимости от того, где находится config.py
project_root = os.path.abspath(os.path.join(current_dir, "../../"))

# Добавляем корневой каталог в sys.path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams

from domain.models.nearest_neighbor import NearestNeighbor
from domain.models.segment import Segment
from domain.types.category import Category
from domain.types.direction import Direction
from domain.types.payload import Payload
from marker.marker import Marker
from services.estimator.reversal_estimator import ReversalEstimator
from services.repository.interface import Repository
from utils.normalized import normalized
from utils.read_data import read_data
from utils.vector_to_point import segment_to_point


@dataclass
class SearchResult:
    """Result of vector similarity search in the space."""

    id: str
    score: float
    payload: Dict[str, Any]
    vector: Optional[List[float]] = None


class QdrantRepository(Repository):
    """
    Vector space for trading patterns.

    Manages 24-dimensional vectors representing trading patterns with:
    - Pattern characteristics (form, position, volume, MA context)
    - Similarity search for pattern matching
    - Efficient storage and retrieval
    """

    def __init__(
        self,
        symbol: str,
        client: Optional[QdrantClient] = None,
        last_id: int = 0,
    ):
        """
        Initialize vector space for specific trading symbol.

        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT', 'ETHUSDT')
            config: Qdrant configuration (if None, creates from env)
            client: Pre-configured QdrantClient (if None, creates from config)
        """
        # Set up basic logging configuration
        logging.basicConfig(
            level=logging.WARNING,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        self.last_id = last_id

        # Validate and normalize symbol
        self.collection_name = symbol

        self.logger = logging.getLogger(__name__)

        # Initialize Qdrant client
        self.client = client or QdrantClient(url=f"http://localhost:6333")

        # Ensure collection exists
        self._ensure_collection()

    def validate_symbol(self, symbol: str) -> str:
        """
        Validate and normalize trading symbol.

        Args:
            symbol: Trading symbol to validate
        """
        if len(symbol) < 1 or len(symbol) > 20:
            raise ValueError("Symbol length must be between 1 and 20 characters.")

        return symbol.upper()

    def _ensure_collection(self):
        """
        Ensure the Qdrant collection for the symbol exists, create if not.
        """
        try:
            # Check if the collection already exists
            self.client.get_collection(self.collection_name)
            self.logger.info(f"Collection '{self.collection_name}' already exists.")
        except Exception as e:
            # If get_collection fails, it likely means the collection doesn't exist.
            # Create a new one.
            self.logger.info(
                f"Collection '{self.collection_name}' not found. Creating a new one."
            )
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=24, distance=Distance.COSINE),  # type: ignore
            )

    def upsert(self, id: int, segment: Segment):
        """
        Upsert a point into the collection.

        Args:
            segment: Segment to upsert
        """
        self.client.upsert(
            collection_name=self.collection_name,
            points=[segment_to_point(id, segment)],
        )

    def count_all(self) -> int:
        """
        Count all vectors in the collection.

        Returns:
            Total number of vectors in the collection
        """
        count_result = self.client.count(
            collection_name=self.collection_name,
            count_filter=None,
            exact=True,
        )

        return count_result.count

    def get_payload(self, id: int) -> Payload:
        """
        Get the payload of a vector by its ID.

        Args:
            id: ID of the vector to retrieve the payload for

        Returns:
            Payload associated with the vector
        """
        result = self.client.retrieve(
            collection_name=self.collection_name,
            ids=[id],
            with_payload=True,
            with_vectors=False,
        )

        if not result:
            return Payload()

        raw = result[0].payload or {}

        category_str = str(raw.get("category", "none")).lower()
        try:
            category = Category(category_str)
        except ValueError:
            category = Category.NONE

        return Payload(
            category=category,
            profit=float(raw.get("profit") or 0.0),
            risk=float(raw.get("risk") or 0.0),
            profit_risk_ratio=float(raw.get("profit_risk_ratio") or 0.0),
        )

    def neighbors(self, id: int, limit: int) -> List[NearestNeighbor]:
        """
        Find similar vectors (neighbors) for a given vector ID.

        Args:
            id: ID of the vector to find neighbors for
            limit: Maximum number of neighbors to return

        Returns:
            SearchResult containing the neighbors' information
        """
        result: List[NearestNeighbor] = []
        nearest_neighbors = self.client.query_points(
            collection_name=self.collection_name,
            query=id,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )

        for point in nearest_neighbors.points:
            raw_payload = point.payload or {}
            result.append(
                NearestNeighbor(
                    id=point.id if isinstance(point.id, int) else int(point.id),
                    score=point.score or 0.0,
                    payload=Payload(
                        category=Category(raw_payload.get("category", "none")),
                        profit=(
                            float(raw_payload["profit"])
                            if raw_payload.get("profit") is not None
                            else 0.0
                        ),
                        risk=(
                            float(raw_payload["risk"])
                            if raw_payload.get("risk") is not None
                            else 0.0
                        ),
                        profit_risk_ratio=(
                            float(raw_payload["profit_risk_ratio"])
                            if raw_payload.get("profit_risk_ratio") is not None
                            else 0.0
                        ),
                    ),
                )
            )

        return result

    def update_payload(self, id: int, payload: Payload):
        """
        Update an existing point in the collection.

        Args:
            point: PointStruct to update
        """
        try:
            self.client.set_payload(
                collection_name=self.collection_name,
                payload=payload.to_dict(),
                points=[id],
            )
        except Exception as e:
            print(f"Error updating payload for id={id}: {e}")

    def delete_collection(self, collection_name: str):
        """
        Delete the entire collection.

        Args:
            collection_name: Name of the collection to delete
        """
        self.client.delete_collection(collection_name=collection_name)

    def delete_vector(self, id: int):
        """
        Delete a specific vector by its ID.

        Args:
            id: ID of the vector to delete
        """
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=[id],
        )

    def clear_collection(self):
        """
        Clear all points from the collection.
        """
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(filter=models.Filter()),  # type: ignore
            wait=True,
        )

    def clean_expired(self, when: datetime):
        """
        Clean up expired vectors based on their 'expire_at' field in the payload.
        """

        # Delete points matching the filter condition
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="expire_at",
                            range=models.DatetimeRange(lte=when),
                        )
                    ]
                )
            ),
            wait=True,
        )


if __name__ == "__main__":
    collection_name = normalized("btcusdt")
    qdrant_repository = QdrantRepository(symbol=collection_name)

    a_len = 4
    base_offset_hours = 0
    base_period_hours = 48
    input_file = "data/candles/BTCUSDT/ma_added/BTCUSDT_5m_ma.csv"

    base_df = read_data(
        input_file=input_file,
        offset_hours=base_offset_hours,
        limit_hours=base_period_hours,
    )
    estimator = ReversalEstimator()
    marker = Marker(estimator=estimator, a_len=a_len)
    base_segments = marker.mark(base_df)
    print(f"Сегментов найдено = {len(base_segments)}")
    base_vectors = []

    for idx, segment in enumerate(base_segments):
        segment.update_pattern_characteristics(
            candles_limit=a_len,
            ma_50s=base_df["ma_50"].tolist(),
            ma_200s=base_df["ma_200"].tolist(),
        )

        qdrant_repository.upsert(id=idx, segment=segment)

    # qdrant_repository.delete_collection(collection_name=collection_name)
    qdrant_repository.update_payload(
        id=1,
        payload=Payload(
            category=Category.BEAR, profit=10.0, risk=5.0, profit_risk_ratio=200
        ),
    )
    results = qdrant_repository.neighbors(id=3, limit=5)

    for res in results:
        print(f"id: {res.id}, score: {res.score}, payload: {res.payload}")

    # space.clean_expired(when=datetime.now(timezone.utc))
