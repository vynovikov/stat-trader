import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, Tuple

from domain.types.direction import Direction


@dataclass
class Point:
    """
    Точка на векторной плоскости.
    Представляет собой паттерн движения цены с определенным направлением.
    """

    x: float
    y: float
    direction: Direction
    id: int = 0
    group_id: int = field(
        default=-1
    )  # Используем field для явного указания значения по умолчанию
    is_corrupted: bool = False
    neighbors: Dict[int, "Point"] = field(default_factory=dict)
    sl: float = 0.0
    tp: float = 0.0

    def __post_init__(self):
        """
        Инициализация после создания объекта.
        """
        # Убеждаемся, что neighbors - это словарь
        if not isinstance(self.neighbors, dict):
            self.neighbors = {}

    def corruption_check(self) -> None:
        """
        Проверяет, является ли точка "испорченной" на основе расстояний до соседей.

        Точка считается испорченной, если ближайший сосед с противоположным направлением
        находится ближе, чем ближайший сосед с тем же направлением.
        """
        closest_same_direction = float("inf")
        closest_opposite_direction = float("inf")

        for _, neighbor in self.neighbors.items():
            distance = self.distance(neighbor)

            if neighbor.direction == self.direction:
                closest_same_direction = min(closest_same_direction, distance)
            else:
                closest_opposite_direction = min(closest_opposite_direction, distance)

        if (
            closest_same_direction != float("inf")
            and closest_opposite_direction != float("inf")
            and closest_opposite_direction < closest_same_direction
        ):
            self.is_corrupted = True

    def difference(self, other: "Point") -> Tuple[float, float]:
        """
        Вычисляет разницу между текущей точкой и другой точкой.

        Args:
            other: Другая точка для сравнения

        Returns:
            Кортеж из разницы по x и y
        """
        dx = other.x - self.x
        dy = other.y - self.y

        return dx, dy

    def distance(self, other: "Point") -> float:
        dx, dy = self.difference(other)

        return (dx * dx + dy * dy) ** 0.5

    def sector(self, other: "Point", sector_size: float) -> int:
        if sector_size <= 0:
            raise ValueError("Sector size must be greater than 0")

        dx, dy = self.difference(other)

        angle_deg = math.degrees(math.atan2(dy, dx))
        if angle_deg < 0:
            angle_deg += 360

        return int(angle_deg / sector_size) * int(sector_size)

    def min_distance_to_counter_direction(self) -> float:
        """
        Вычисляет минимальное расстояние до ближайшей точки в противоположном направлении.
        Если нет соседей в противоположном направлении, возвращает 0.
        """
        closest_opposite_distance = -1

        for neighbor in self.neighbors.values():
            if neighbor.direction != self.direction:
                distance = self.distance(neighbor)
                if (
                    closest_opposite_distance == -1
                    or distance < closest_opposite_distance
                ):
                    closest_opposite_distance = distance

        return closest_opposite_distance
