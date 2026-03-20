# Руководство по качественному отображению торговых сегментов

## 📋 Содержание

1. [Векторизация сегментов](#векторизация-сегментов)
2. [Размещение на плоскости](#размещение-на-плоскости)
3. [Обеспечение равномерности](#обеспечение-равномерности)
4. [Группировка и визуализация](#группировка-и-визуализация)
5. [Типичные проблемы и решения](#типичные-проблемы-и-решения)

---

## 🔧 Векторизация сегментов

### Принципы качественной векторизации

#### 1. **Детализированное описание каждой свечи**
```python
# ✅ ПРАВИЛЬНО: 44-параметрическая векторизация
# Для каждой из 8 свечей прелюдии:
- body_ratio = body_size / full_length           # Размер тела
- upper_shadow_ratio = upper_shadow / full_length # Верхняя тень
- lower_shadow_ratio = lower_shadow / full_length # Нижняя тень
- relative_position = (mid_price - first_mid) / range # Позиция
- relative_volume = volume / avg_volume          # Объем

# ❌ НЕПРАВИЛЬНО: агрегированные характеристики
- avg_body_ratio, max_shadow, total_volume       # Теряет детали
```

#### 2. **Структура вектора (44 параметра)**
```python
vector = [
    # ФОРМА СВЕЧЕЙ (24 параметра = 8 свечей × 3 характеристики)
    body_ratios[0:8],         # Размеры тел свечей
    upper_shadow_ratios[0:8], # Верхние тени
    lower_shadow_ratios[0:8], # Нижние тени

    # ОТНОСИТЕЛЬНОЕ РАСПОЛОЖЕНИЕ (8 параметров)
    relative_positions[0:8],  # Позиции mid_price

    # ОБЪЕМЫ (8 параметров)
    relative_volumes[0:8],    # Объемы относительно среднего

    # MA КОНТЕКСТ (4 параметра)
    ma50_position,            # Позиция относительно MA50
    ma200_position,           # Позиция относительно MA200
    ma50_trend,              # Тренд MA50
    ma200_trend              # Тренд MA200
]
```

#### 3. **Нормализация признаков**
```python
# ✅ Используйте StandardScaler для входных векторов
feature_scaler = StandardScaler()
normalized_vectors = feature_scaler.fit_transform(raw_vectors)

# ⚠️ ВАЖНО: обучайте скейлер на всем датасете сразу
# Не нормализуйте каждый сегмент отдельно!
```

---

## 🗺️ Размещение на плоскости

### Оптимальные параметры UMAP

#### 1. **Для равномерного распределения**
```python
reducer = UMAP(
    n_components=2,
    n_neighbors=10,        # ✅ 10-15 для менее агрессивной кластеризации
    min_dist=0.3,          # ✅ 0.2-0.5 для равномерности (НЕ 0.05!)
    spread=2.0,            # ✅ 1.5-3.0 для контроля распределения
    metric="euclidean",    # ✅ Стандартная метрика
    random_state=42        # ✅ Воспроизводимость
)
```

#### 2. **Проблемные параметры**
```python
# ❌ ИЗБЕГАЙТЕ этих значений:
n_neighbors=15+,     # Слишком агрессивная кластеризация
min_dist=0.05,       # Точки "слипаются" у краев
# Отсутствие spread  # Нет контроля распределения
```

### Двухэтапное масштабирование

#### 1. **Входные векторы**
```python
# Этап 1: Нормализация признаков
feature_scaler = StandardScaler()
scaled_vectors = feature_scaler.fit_transform(input_vectors)
```

#### 2. **Выходные координаты**
```python
# Этап 2: UMAP проекция
umap_coordinates = reducer.transform(scaled_vectors)

# Этап 3: Масштабирование координат в [-1, 1]
coords_scaler = MinMaxScaler(feature_range=(-1, 1))
final_coordinates = coords_scaler.fit_transform(umap_coordinates)
```

#### ⚠️ **КРИТИЧЕСКИ ВАЖНО**
```python
# ✅ ПРАВИЛЬНО: Единые скейлеры для всех точек
scatter = Scatter.create_with_initial_data(vectors, reducer)
for vector in new_vectors:
    # Используем ТЕ ЖЕ скейлеры
    scaled = scatter.feature_scaler.transform(vector)
    coords = scatter.coords_scaler.transform(reducer.transform(scaled))

# ❌ НЕПРАВИЛЬНО: Разные скейлеры
local_scaler = MinMaxScaler()  # Новый скейлер!
coords = local_scaler.fit_transform(umap_coords)  # Конфликт!
```

---

## ⚖️ Обеспечение равномерности

### Диагностика распределения

#### 1. **Анализ расстояний**
```python
def analyze_distribution(coordinates):
    distances = []
    for i in range(len(coordinates)):
        for j in range(i+1, len(coordinates)):
            dist = np.linalg.norm(coordinates[i] - coordinates[j])
            distances.append(dist)

    print(f"Min distance: {min(distances):.6f}")
    print(f"Max distance: {max(distances):.6f}")
    print(f"Mean distance: {np.mean(distances):.6f}")
    print(f"Std distance: {np.std(distances):.6f}")

    # ✅ Хорошее распределение: std/mean < 0.5
    # ❌ Плохое распределение: std/mean > 1.0
```

#### 2. **Визуальная проверка**
```python
# Создайте тепловую карту плотности
plt.hexbin(coordinates[:, 0], coordinates[:, 1], gridsize=20)
plt.colorbar(label='Density')

# ✅ Равномерное: плотность везде примерно одинаковая
# ❌ Неравномерное: ярко выраженные "горячие" зоны
```

### Адаптивный scan_radius

#### 1. **k-NN алгоритм**
```python
def calculate_scan_radius_knn(coordinates, target_neighbors=4):
    if len(coordinates) < target_neighbors + 1:
        return 0.1

    # k-NN поиск
    k = min(target_neighbors + 1, len(coordinates))
    nbrs = NearestNeighbors(n_neighbors=k).fit(coordinates)
    distances, _ = nbrs.kneighbors(coordinates)

    # Расстояния до k-го соседа
    kth_distances = distances[:, -1]

    # ✅ Для равномерного распределения: множитель 3.0-4.0
    # ❌ Для кластерного распределения: множитель 1.2-1.5
    return float(np.median(kth_distances) * 4.0)
```

#### 2. **Адаптация к параметрам UMAP**
```python
# Соответствие scan_radius и UMAP параметров:
if min_dist >= 0.3 and spread >= 2.0:
    scan_radius_multiplier = 3.0-4.0  # Равномерное распределение
elif min_dist <= 0.1:
    scan_radius_multiplier = 1.2-1.5  # Кластерное распределение
else:
    scan_radius_multiplier = 2.0-2.5  # Промежуточное
```

---

## 🎨 Группировка и визуализация

### Корректная группировка

#### 1. **Логика group_id**
```python
# ✅ ПРАВИЛЬНО: group_id начинается с 0
grouped_points = [p for p in points if p.group_id >= 0]

# ❌ НЕПРАВИЛЬНО: пропускает группу 0
grouped_points = [p for p in points if p.group_id > 0]
```

#### 2. **Избегание двойной группировки**
```python
# ✅ ПРАВИЛЬНО: группировка один раз
scatter = create_base_scatter(reducer, vectors)  # Внутри: scan + group
scatter.visualize("output.png")

# ❌ НЕПРАВИЛЬНО: повторная группировка
scatter = create_base_scatter(reducer, vectors)  # Первая группировка
scatter.scan_all_points()  # Перезапись neighbors
scatter.group()           # Вторая группировка - затирает первую!
```

#### 3. **Счетчик групп**
```python
# ✅ ПРАВИЛЬНО: всегда увеличиваем счетчик
if current_group.is_valid():
    self.groups.append(current_group)
else:
    # Группа невалидна, но счетчик все равно увеличиваем
    for p in current_group.points:
        p.group_id = -1

group_counter += 1  # Всегда!
```

### Визуализация групп

#### 1. **Цветовая схема**
```python
# Точки
if point.direction.name == "UP":
    color = "green"
elif point.direction.name == "DOWN":
    color = "red"

# Линии групп
if group.direction.name == "UP":
    border_color = "darkgreen"  # Темнее для контраста
else:
    border_color = "darkred"
```

#### 2. **Прозрачность**
```python
# ✅ Сгруппированные точки ярче
alpha = 0.8 if point.group_id >= 0 else 0.5

# Линии групп
plt.plot(points[:, 0], points[:, 1],
         color=border_color, alpha=0.9, linewidth=2)
```

---

## ⚠️ Типичные проблемы и решения

### Проблема 1: Точки скапливаются у краев
```python
# 🔍 СИМПТОМЫ:
- Плотные кластеры у границ [-1, 1]
- Пустота в центре
- std/mean расстояний > 1.0

# ✅ РЕШЕНИЕ:
reducer = UMAP(
    min_dist=0.3,    # Увеличить с 0.05
    spread=2.0,      # Добавить параметр
    n_neighbors=10   # Уменьшить с 15+
)
```

### Проблема 2: Группы не отображаются
```python
# 🔍 СИМПТОМЫ:
- Точки разной яркости, но нет линий
- Статистика показывает 0 групп
- В логах: "Группировка завершена: создано X групп"

# ✅ РЕШЕНИЕ:
# 1. Проверить двойную группировку
# 2. Проверить условие group_id >= 0 (не > 0)
# 3. Убедиться что groups не очищается после создания
```

### Проблема 3: Неправильный scan_radius
```python
# 🔍 СИМПТОМЫ:
- Много несгруппированных точек
- scan_radius << средние расстояния
- Или наоборот: все точки в одной группе

# ✅ РЕШЕНИЕ:
# Адаптировать множитель под распределение:
if mean_distance > 0.5:  # Равномерное распределение
    multiplier = 4.0
else:                     # Кластерное распределение
    multiplier = 1.5

scan_radius = np.median(kth_distances) * multiplier
```

### Проблема 4: Конфликт скейлеров
```python
# 🔍 СИМПТОМЫ:
- Координаты точек не соответствуют ожидаемым
- Группировка работает в коде, но не на графике
- Разные результаты при повторных запусках

# ✅ РЕШЕНИЕ:
# Использовать единую систему скейлеров:
scatter = Scatter.create_with_initial_data(vectors, reducer)
# Все последующие точки обрабатывать через scatter.feature_scaler
# и scatter.coords_scaler
```

---

## 📊 Метрики качества

### Оценка равномерности
```python
def evaluate_uniformity(coordinates):
    # 1. Коэффициент вариации расстояний
    distances = calculate_all_distances(coordinates)
    cv = np.std(distances) / np.mean(distances)

    # 2. Индекс кластеризации (Hopkins statistic)
    hopkins = calculate_hopkins_statistic(coordinates)

    # 3. Плотность по квадрантам
    density_variance = calculate_quadrant_density_variance(coordinates)

    return {
        'cv_distances': cv,        # ✅ < 0.5 хорошо
        'hopkins': hopkins,        # ✅ ~0.5 равномерно
        'density_var': density_variance  # ✅ < 0.1 хорошо
    }
```

### Оценка группировки
```python
def evaluate_grouping(scatter):
    total_points = len(scatter.points)
    grouped_points = sum(1 for p in scatter.points if p.group_id >= 0)

    return {
        'grouping_rate': grouped_points / total_points,  # ✅ 20-30% оптимально
        'num_groups': len(scatter.groups),               # Зависит от данных
        'avg_group_size': grouped_points / len(scatter.groups),  # ✅ 3-8 хорошо
        'direction_separation': calculate_direction_separation(scatter)  # ✅ > 0.8
    }
```

---

## 🎯 Чек-лист качественной визуализации

### ✅ Векторизация
- [ ] 44-параметрический вектор (не агрегированные характеристики)
- [ ] StandardScaler для входных векторов
- [ ] Единый скейлер для всего датасета

### ✅ UMAP проекция
- [ ] `min_dist=0.3` (не 0.05!)
- [ ] `spread=2.0`
- [ ] `n_neighbors=10` (не 15+)
- [ ] MinMaxScaler для координат в [-1, 1]

### ✅ Группировка
- [ ] scan_radius рассчитан после размещения точек
- [ ] Множитель 3.0-4.0 для равномерного распределения
- [ ] `group_id >= 0` в условиях (не `> 0`)
- [ ] Один вызов `group()`, не два

### ✅ Визуализация
- [ ] Линии групп отображаются
- [ ] Сгруппированные точки ярче (alpha=0.8)
- [ ] Правильная статистика в углу
- [ ] Debug режим с ID точек и групп

---

*Последнее обновление: декабрь 2024*
*Версия системы: 44-параметрическая векторизация с оптимизированным UMAP*