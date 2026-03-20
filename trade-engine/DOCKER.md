# Docker для Trade-Engine

## Сборка образа

```bash
docker build -t trade-engine:latest .
```

## Запуск контейнера

```bash
docker run -d \
  --name trade-engine \
  -p 5002:5002 \
  -e SYMBOL=BTCUSDT \
  -e TIMEFRAME=5m \
  -e LOCAL_ADDR=:5002 \
  -e BACKEND_ADDR=stock-interactor:5001 \
  -e QDRANT_HOST=qdrant \
  -e QDRANT_PORT=6333 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  trade-engine:latest
```

## Переменные окружения

### Основные параметры

| Переменная | Описание | Пример |
|-----------|----------|--------|
| `SYMBOL` | Торговый символ | `BTCUSDT` |
| `TIMEFRAME` | Таймфрейм свечей | `5m`, `1m` |
| `LOCAL_ADDR` | Адрес gRPC сервера | `:5002` |
| `BACKEND_ADDR` | Адрес stock-interactor | `localhost:5001` |

### Qdrant Configuration

| Переменная | Описание | Значение по умолчанию |
|-----------|----------|----------------------|
| `QDRANT_HOST` | Хост Qdrant | `localhost` |
| `QDRANT_PORT` | REST API порт | `6333` |
| `QDRANT_GRPC_PORT` | gRPC порт | `6334` |
| `VECTOR_DIMENSION` | Размерность векторов | `44` |
| `DISTANCE_METRIC` | Метрика расстояния | `Cosine` |

### ML Parameters

| Переменная | Описание | Значение по умолчанию |
|-----------|----------|----------------------|
| `A_LEN` | Длина вектора A | `8` |
| `WINDOW_SIZE` | Размер окна | `100` |

### Deal Status Codes

| Переменная | Описание | Пример |
|-----------|----------|--------|
| `BUY_TP` | Код для покупки с прибылью | `BUY_TP` |
| `SELL_TP` | Код для продажи с прибылью | `SELL_TP` |
| `BUY_LOSS` | Код для покупки с убытком | `BUY_LOSS` |
| `SELL_LOSS` | Код для продажи с убытком | `SELL_LOSS` |
| `BUY_SL` | Код для покупки со стоп-лоссом | `BUY_SL` |
| `SELL_SL` | Код для продажи со стоп-лоссом | `SELL_SL` |

## Порты

- `5002` - gRPC сервер (trade-engine)

## Особенности сборки

### Двухуровневая сборка (Multi-stage build)

**Stage 1: Builder**
- Базовый образ: `python:3.12-slim`
- Установка компиляторов (gcc, g++) для сборки ML-библиотек
- Установка Python зависимостей в отдельную директорию
- Генерация protobuf файлов

**Stage 2: Runtime**
- Базовый образ: `python:3.12-slim`
- Только runtime зависимости (libgomp1)
- Копирование установленных пакетов из builder
- Непривилегированный пользователь `appuser`

### Размер образа

Финальный образ: **~926 MB**

Размер обусловлен ML-библиотеками:
- numpy, pandas, scipy
- scikit-learn
- umap-learn
- matplotlib

### Безопасность

- ✅ Непривилегированный пользователь (UID 1000)
- ✅ Минимальный базовый образ (slim)
- ✅ Удаление кэша apt и pip
- ✅ Только runtime зависимости в финальном образе

## Volumes

### Рекомендуемые монтирования

```bash
-v ./data:/app/data          # Данные для обучения/тестирования
-v ./models:/app/models      # Сохраненные ML модели
```

## Точки входа

По умолчанию запускается `services/grpc_server/grpc_server_con_v2_con_v3.py`.

Для запуска другого сервера переопределите CMD:

```bash
docker run -d \
  --name trade-engine \
  -p 5010:5010 \
  trade-engine:latest \
  python -u services/grpc_server/grpc_server_con_v2_rev_v4.py
```

## Отладка

### Просмотр логов

```bash
docker logs -f trade-engine
```

### Интерактивный shell

```bash
docker exec -it trade-engine bash
```

### Проверка здоровья

```bash
# Проверка, что gRPC сервер отвечает
grpcurl -plaintext localhost:5002 list
```

### Проверка зависимостей

```bash
docker exec -it trade-engine pip list
```

## Docker Compose

Для использования с docker-compose см. обновленный файл `docker-compose.yml` в корне проекта vector-trader.

## Зависимости от других сервисов

Trade-engine зависит от:
1. **stock-interactor** - для получения данных свечей (gRPC)
2. **qdrant** - векторная база данных для хранения паттернов

Убедитесь, что эти сервисы запущены и доступны перед запуском trade-engine.

