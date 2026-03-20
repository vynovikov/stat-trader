from typing import Union, cast

import numpy as np
import umap
from sklearn.preprocessing import StandardScaler

# Уточняем возвращаемый тип функции для статического анализатора
# Она может вернуть либо np.ndarray, либо кортеж из np.ndarray и umap.UMAP
ReturnType = Union[np.ndarray, tuple[np.ndarray, umap.UMAP]]


def structure_to_umap_point(
    data_array: np.ndarray, target_row_index: int, umap_model: umap.UMAP | None = None
) -> ReturnType:
    """
    Преобразует строку из NumPy массива в 2D-точку UMAP.

    Параметры:
    data_array (np.ndarray): Входной NumPy массив, содержащий числовые признаки.
                             Ожидается 2D-массив (строки x столбцы).
    target_row_index (int): Индекс строки в data_array, которую нужно преобразовать.
    umap_model (umap.UMAP, optional): Обученная модель UMAP. Если None, новая модель будет обучена
                                     на всем data_array. По умолчанию None.

    Возвращает:
    np.ndarray: 2D-координаты UMAP для целевой строки.
    umap.UMAP: Обученная модель UMAP (возвращается, если umap_model был None).
    """

    if not isinstance(data_array, np.ndarray):
        raise TypeError("Входная data_array должна быть np.ndarray.")
    if data_array.ndim != 2:
        raise ValueError(
            "Входной data_array должен быть 2D-массивом (строки x столбцы)."
        )
    if not 0 <= target_row_index < len(data_array):
        raise IndexError(
            "target_row_index находится за пределами диапазона data_array."
        )

    # 1. Подготовка данных: Масштабирование числовых признаков
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data_array)

    embedding: np.ndarray  # Объявляем переменную здесь
    actual_umap_model: (
        umap.UMAP
    )  # Переменная для хранения фактически используемой/обученной модели UMAP

    # 2. Обучение или использование UMAP модели
    if umap_model is None:
        print("Обучение новой модели UMAP...")

        n_rows = len(scaled_data)
        # UMAP требует n_neighbors >= 1. Если n_components > 0, он также часто требует n_neighbors >= n_components.
        # Для 2 компонентов, n_neighbors >= 2.
        # Если строк мало, n_neighbors должен быть <= n_rows - 1.

        # Минимально рекомендованное количество соседей для UMAP, чтобы получить 2D-вложение
        # Если данных очень мало (2-3 строки), UMAP может вести себя странно.
        # min_n_neighbors_for_2d_embedding = max(2, n_components_requested)
        # UMAP по умолчанию n_neighbors=15

        # Если у нас 2 строки, n_neighbors_val будет 1. UMAP может выдать предупреждение, но работать.
        # Если 1 строка, то n_rows - 1 = 0, и это вызовет ошибку.
        if n_rows < 2:
            raise ValueError(
                f"Недостаточно данных для UMAP. Требуется минимум 2 строки. Получено {n_rows}."
            )

        n_neighbors_val = min(15, n_rows - 1)
        # Если n_neighbors_val становится 1 (для 2 строк данных), UMAP может выдать предупреждение,
        # что n_neighbors меньше, чем ожидается для n_components.
        # Мы оставляем n_neighbors_val=1 для 2 строк, позволяя UMAP предупредить,
        # чтобы пользователь знал о потенциальной деградации качества вложения.

        actual_umap_model = umap.UMAP(
            n_components=2, random_state=42, n_neighbors=n_neighbors_val
        )

        embedding = cast(np.ndarray, actual_umap_model.fit_transform(scaled_data))

        # Дополнительная проверка, чтобы убедиться, что UMAP вернул 2D-вложение
        if embedding.ndim != 2 or embedding.shape[1] != 2:
            # Если UMAP не смог создать 2D-вложение (например, если он сделал его 1D)
            raise RuntimeError(
                f"UMAP не вернул ожидаемое 2D-вложение. Получена форма: {embedding.shape}. "
                f"Исходная форма данных: {scaled_data.shape}. "
                f"Это может произойти при очень малом количестве данных или недостаточной вариативности."
            )

    else:
        print("Использование существующей модели UMAP...")
        # Убедимся, что переданный umap_model является экземпляром UMAP
        if not isinstance(umap_model, umap.UMAP):
            raise TypeError(
                f"Переданный 'umap_model' не является объектом umap.UMAP. Получен тип: {type(umap_model)}"
            )
        actual_umap_model = umap_model
        embedding = cast(np.ndarray, actual_umap_model.transform(scaled_data))

        # Проверка формы также для transform, на случай если что-то пошло не так
        if embedding.ndim != 2 or embedding.shape[1] != 2:
            raise RuntimeError(
                f"UMAP transform не вернул ожидаемое 2D-вложение. Получена форма: {embedding.shape}. "
                f"Проверьте обученную модель и входные данные."
            )

    # 3. Извлечение UMAP-точки для целевой строки
    umap_point = embedding[target_row_index]

    if umap_model is None:
        # Если мы обучили новую модель, возвращаем точку и эту модель
        return umap_point, actual_umap_model
    else:
        # Если мы использовали существующую модель, возвращаем только точку
        return umap_point


if __name__ == "__main__":
    # Пример использования:
    data = np.array(
        [
            [10, 1.5, 100],
            [20, 2.3, 200],
            [12, 1.8, 110],
            [22, 2.5, 210],
            [11, 1.7, 105],
            [19, 2.1, 195],
        ]
    )
    print("Исходный NumPy массив:")
    print(data)
    print("-" * 30)

    # --- Сценарий 1: Обучение новой модели UMAP и преобразование ---
    print("Сценарий 1: Обучение новой модели UMAP для преобразования строки 0")
    target_index_1 = 0
    # Здесь мы ожидаем кортеж, так как umap_model был None
    umap_point_1, trained_umap_model = structure_to_umap_point(data, target_index_1)
    print(f"UMAP-точка для строки {target_index_1}: {umap_point_1}")
    print(f"Тип UMAP-точки: {type(umap_point_1)}, Форма: {umap_point_1.shape}")
    print(f"Тип обученной модели: {type(trained_umap_model)}")  # Добавлено для отладки
    print("-" * 30)

    # --- Сценарий 2: Использование обученной модели UMAP для преобразования другой строки ---
    print("Сценарий 2: Использование обученной модели UMAP для преобразования строки 2")
    target_index_2 = 2
    # Здесь мы ожидаем только np.ndarray, так как передаем umap_model
    umap_point_2 = cast(
        np.ndarray,
        structure_to_umap_point(data, target_index_2, umap_model=trained_umap_model),
    )
    print(f"UMAP-точка для строки {target_index_2}: {umap_point_2}")
    print(f"Тип UMAP-точки: {type(umap_point_2)}, Форма: {umap_point_2.shape}")
    print("-" * 30)

    # --- Сценарий 3: Попытка преобразовать массив с неверной размерностью (ожидается ошибка) ---
    print("Сценарий 3: Попытка с 1D-массивом (ожидается ошибка)...")
    data_1d = np.array([1, 2, 3])
    try:
        structure_to_umap_point(data_1d, 0)
    except ValueError as e:
        print(f"Перехвачена ожидаемая ошибка: {e}")
    print("-" * 30)

    # --- Сценарий 4: Попытка с недостаточным количеством данных (ожидается ошибка) ---
    print(
        "Сценарий 4: Попытка с недостаточным количеством данных (ожидается ошибка)..."
    )
    data_small_1_row = np.array([[10, 1.5, 100]])  # Одна строка данных
    try:
        structure_to_umap_point(data_small_1_row, 0)
    except ValueError as e:
        print(f"Перехвачена ожидаемая ошибка: {e}")
    print("-" * 30)

    print(
        "Сценарий 5: Попытка с двумя строками данных (UMAP может выдать предупреждение, но должен работать)"
    )
    data_two_rows = np.array([[10, 1.5, 100], [20, 2.3, 200]])  # Две строки данных
    try:
        # Для этого сценария мы ожидаем кортеж (точка, модель), т.к. модель не передаем
        umap_point_two_rows, _ = structure_to_umap_point(data_two_rows, 0)
        print(
            f"UMAP-точка для строки 0 (малый датасет из 2х строк): {umap_point_two_rows}"
        )
        print(
            f"Тип UMAP-точки: {type(umap_point_two_rows)}, Форма: {umap_point_two_rows.shape}"
        )
    except Exception as e:
        print(f"Перехвачена ошибка: {e}")
    print("-" * 30)
