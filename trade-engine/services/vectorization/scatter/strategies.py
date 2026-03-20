from collections import deque
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Set, Tuple

if TYPE_CHECKING:
    from ....domain.models.group import Group
    from ....domain.types.point import Direction, Point
    from ...scatter.scatter import Scatter
else:
    from domain.models.group import Group


@dataclass
class GroupingStrategy:
    """
    Базовый класс для стратегий группировки точек.
    """

    min_group_size: int = 3

    def create_groups(self, points: List["Point"]) -> List["Group"]:
        """
        Создает группы точек используя текущую стратегию

        Args:
            points: Список точек для группировки

        Returns:
            Список созданных групп
        """
        raise NotImplementedError


@dataclass
class CurrentGroupingStrategy(GroupingStrategy):
    """
    Текущая стратегия группировки точек.
    """

    scan_radius: float = 1.0
    sector_size: float = 6.0

    def create_groups(self, points: List["Point"]) -> List["Group"]:
        """
        Создает группы точек используя текущую стратегию

        Args:
            points: Список точек для группировки

        Returns:
            Список созданных групп
        """
        groups = []
        processed = set()
        next_group_id = 1

        # Сначала находим соседей для всех точек используя новый API
        from ...scatter.scatter import Scatter

        temp_scatter = Scatter(
            scan_radius=self.scan_radius,
            sector_size=self.sector_size,
            min_group_size=self.min_group_size,
        )
        temp_scatter.points = points
        temp_scatter.sorted_x = sorted(
            [(p.id, p.x) for p in points], key=lambda x: x[1]
        )
        temp_scatter.sorted_y = sorted(
            [(p.id, p.y) for p in points], key=lambda x: x[1]
        )

        for point in points:
            temp_scatter.scan(point)

        # Создаем группы
        for start_point in points:
            if start_point.id in processed:
                continue

            # Создаем новую группу
            group = Group(
                id=next_group_id,
                direction=start_point.direction,
                min_size=self.min_group_size,
            )

            # Используем очередь для итеративного обхода
            queue = deque([start_point])
            while queue:
                point = queue.popleft()
                if point.id in processed:
                    continue

                # Обрабатываем точку
                processed.add(point.id)
                point.group_id = group.id
                group.add_point(point)

                # Добавляем необработанных соседей того же направления
                for _, neighbor in point.neighbors.items():
                    if (
                        neighbor.id not in processed
                        and neighbor.direction == group.direction
                    ):
                        queue.append(neighbor)

            # Проверяем валидность группы
            if group.is_valid():
                groups.append(group)
                next_group_id += 1
            else:
                # Помечаем точки как обработанные, но не в группе
                for p in group.points:
                    p.group_id = -1

        return groups


@dataclass
class BFSGroupingStrategy(GroupingStrategy):
    """
    Стратегия группировки на основе поиска в ширину (BFS):
    1. Для каждой точки находятся соседи в заданном радиусе
    2. Начиная с непосещенной точки, запускаем BFS
    3. BFS формирует группу, добавляя соседние точки того же направления
    """

    scan_radius: float = 1.0
    sector_size: float = 6.0
    visited: Set[int] = field(default_factory=set, init=False)
    next_group_id: int = field(default=1, init=False)

    def create_groups(self, points: List["Point"]) -> List["Group"]:
        """
        Создает группы точек используя BFS

        Args:
            points: Список точек для группировки

        Returns:
            Список созданных групп
        """
        # Сначала находим соседей для всех точек используя новый API
        from ...scatter.scatter import Scatter

        temp_scatter = Scatter(
            scan_radius=self.scan_radius,
            sector_size=self.sector_size,
            min_group_size=self.min_group_size,
        )
        temp_scatter.points = points
        temp_scatter.sorted_x = sorted(
            [(p.id, p.x) for p in points], key=lambda x: x[1]
        )
        temp_scatter.sorted_y = sorted(
            [(p.id, p.y) for p in points], key=lambda x: x[1]
        )

        for point in points:
            temp_scatter.scan(point)

        # Инициализируем структуры данных для BFS
        groups = []
        self.visited.clear()
        self.next_group_id = 1

        # Проходим по всем точкам
        for start_point in points:
            if start_point.id in self.visited:
                continue

            # Создаем новую группу
            current_group = Group(
                id=self.next_group_id,
                direction=start_point.direction,
                min_size=self.min_group_size,
            )

            # Инициализируем очередь для BFS
            queue = deque([start_point])
            self.visited.add(start_point.id)
            current_group.add_point(start_point)
            start_point.group_id = current_group.id

            # Запускаем BFS
            while queue:
                current_point = queue.popleft()

                # Проверяем всех соседей
                for _, neighbor in current_point.neighbors.items():
                    if (
                        neighbor.id not in self.visited
                        and neighbor.direction == current_group.direction
                    ):
                        self.visited.add(neighbor.id)
                        queue.append(neighbor)
                        current_group.add_point(neighbor)
                        neighbor.group_id = current_group.id

            # Если группа достаточно большая, сохраняем её
            if current_group.is_valid():
                groups.append(current_group)
                self.next_group_id += 1
            else:
                # Помечаем точки как не входящие в группу
                for point in current_group.points:
                    point.group_id = -1

        return groups
