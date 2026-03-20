from enum import Enum

import numpy as np
from sklearn.neighbors import KNeighborsClassifier


class PatternAnalyzer:
    def __init__(self, dominance_threshold=0.75, n_neighbors=10, grid_size=20):
        """
        Инициализация анализатора паттернов.

        Args:
            dominance_threshold: порог доминирования направления (0.75 = 75%)
            n_neighbors: количество соседей для анализа области
            grid_size: размер сетки для разбиения пространства
        """
        self.dominance_threshold = dominance_threshold
        self.n_neighbors = n_neighbors
        self.grid_size = grid_size
        self.knn = KNeighborsClassifier(n_neighbors=n_neighbors, weights="distance")

    def fit(self, tsne_coords, directions):
        """
        Обучает классификатор на данных t-SNE.

        Args:
            tsne_coords: координаты точек после t-SNE
            directions: список направлений движения
        """
        self.tsne_coords = tsne_coords
        self.directions = directions

        # Преобразуем направления в числовые метки
        self.direction_labels = [
            1 if str(d) == "Direction.UP" else 0 for d in directions
        ]
        self.knn.fit(tsne_coords, self.direction_labels)

        return self

    def predict_proba(self, points):
        """
        Предсказывает вероятности направлений для заданных точек.

        Args:
            points: массив точек для предсказания

        Returns:
            probas: массив вероятностей для направления UP
        """
        # Получаем индексы k ближайших соседей и их веса
        distances, indices = self.knn.kneighbors(points)
        weights = 1 / (
            distances + 1e-6
        )  # Добавляем эпсилон чтобы избежать деления на 0

        # Нормализуем веса
        weights = weights / weights.sum(axis=1, keepdims=True)

        # Считаем взвешенную сумму меток (1 для UP, 0 для DOWN)
        probas = np.zeros(len(points))
        for i in range(len(points)):
            neighbor_labels = [self.direction_labels[idx] for idx in indices[i]]
            probas[i] = np.sum(weights[i] * neighbor_labels)

        return probas

    def find_dominant_areas(self):
        """
        Находит области с преобладающим направлением, используя сетку.

        Returns:
            mask: маска для точек, находящихся в областях с преобладающим направлением
            probas: вероятности для каждой точки
        """
        # Получаем вероятности для всех точек
        probas = self.predict_proba(self.tsne_coords)

        # Находим точки, где одно из направлений преобладает
        dominant_mask = (probas >= self.dominance_threshold) | (
            probas <= (1 - self.dominance_threshold)
        )

        return dominant_mask, probas

    def get_filtered_data(self):
        """
        Возвращает только те точки, которые находятся в областях с превалирующим направлением.

        Returns:
            filtered_coords: координаты точек в доминантных областях
            filtered_directions: направления для этих точек
            probabilities: вероятности для каждого направления
        """
        dominant_mask, probabilities = self.find_dominant_areas()

        filtered_coords = self.tsne_coords[dominant_mask]
        filtered_directions = [
            d for i, d in enumerate(self.directions) if dominant_mask[i]
        ]
        filtered_probabilities = probabilities[dominant_mask]

        print(f"Отфильтровано {np.sum(dominant_mask)} точек из {len(self.tsne_coords)}")

        return filtered_coords, filtered_directions, filtered_probabilities
