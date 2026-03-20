# Vector Trader - Docker Deployment

Полная система запуска Vector Trader в Docker контейнерах.

## Архитектура

```
┌─────────────────┐
│   stock-interactor   │ (Go)
│   Port: 5001    │ gRPC Server
│   - Binance API │
│   - WebSocket   │
└────────┬────────┘
         │
         │ gRPC
         ▼
┌─────────────────┐     ┌─────────────┐
│  trade-engine   │────▶│   Qdrant    │
│   Port: 5002    │     │ Ports:      │
│   - ML Models   │     │ 6333 (REST) │
│   - Strategy    │     │ 6334 (gRPC) │
└─────────────────┘     └─────────────┘
```

## Сервисы

1. **stock-interactor** (Go)
   - Взаимодействие с Binance API
   - WebSocket для получения данных в реальном времени
   - gRPC сервер для предоставления данных
   - Размер образа: ~23 MB

2. **trade-engine** (Python)
   - ML модели для анализа паттернов
   - Торговые стратегии
   - gRPC сервер для принятия решений
   - Размер образа: ~926 MB

3. **qdrant**
   - Векторная база данных
   - Хранение и поиск паттернов
   - Официальный образ

## Быстрый старт

### 1. Сборка всех образов

```bash
docker-compose build
```

### 2. Запуск всех сервисов

```bash
docker-compose up -d
```

### 3. Проверка статуса

```bash
docker-compose ps
```

### 4. Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f stock-interactor
docker-compose logs -f trade-engine
docker-compose logs -f qdrant
```

### 5. Остановка

```bash
docker-compose down
```

## Детальная конфигурация

### Переменные окружения

Вы можете создать `.env` файл в корне проекта для переопределения переменных:

```bash
# .env
SYMBOL=BTCUSDT
TIMEFRAME=5m
BINANCE_CANDLES_LIMIT=1000
```

### Volumes (Данные)

По умолчанию монтируются:

- `./trade-engine/data` → `/app/data` (данные для ML)
- `./trade-engine/models` → `/app/models` (сохраненные модели)
- `./trade-engine/qdrant/data` → `/qdrant/storage` (Qdrant данные)

### Порты

| Сервис | Порт | Описание |
|--------|------|----------|
| stock-interactor | 5001 | gRPC API |
| stock-interactor | 6060 | pprof (опционально) |
| trade-engine | 5002 | gRPC API |
| qdrant | 6333 | REST API |
| qdrant | 6334 | gRPC API |

## Разработка

### Пересборка одного сервиса

```bash
# Пересобрать stock-interactor
docker-compose build stock-interactor

# Пересобрать trade-engine
docker-compose build trade-engine
```

### Запуск с пересборкой

```bash
docker-compose up -d --build
```

### Интерактивный shell

```bash
# Stock Interactor
docker exec -it stock_interactor sh

# Trade Engine
docker exec -it trade_engine bash

# Qdrant
docker exec -it qdrant_vector_db sh
```

### Проверка работоспособности

```bash
# Проверка stock-interactor
grpcurl -plaintext localhost:5001 list

# Проверка trade-engine
grpcurl -plaintext localhost:5002 list

# Проверка Qdrant
curl http://localhost:6333/health
```

## Мониторинг

### Использование ресурсов

```bash
docker stats stock_interactor trade_engine qdrant_vector_db
```

### Healthchecks

```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

## Troubleshooting

### Проблема: Сервисы не могут соединиться

**Решение**: Проверьте, что все сервисы в одной сети:

```bash
docker network inspect vector-trader-network
```

### Проблема: trade-engine не может подключиться к stock-interactor

**Решение**: Убедитесь, что `BACKEND_ADDR=stock-interactor:5001` (имя сервиса, а не localhost)

### Проблема: Qdrant не запускается

**Решение**: Проверьте права доступа к директории `./trade-engine/qdrant/data`:

```bash
sudo chown -R 1000:1000 ./trade-engine/qdrant/data
```

### Проблема: Порт уже занят

**Решение**: Измените порты в docker-compose.yml или освободите порты:

```bash
# Проверить, кто использует порт
sudo lsof -i :5001
```

## Остановка и очистка

### Остановка всех сервисов

```bash
docker-compose down
```

### Остановка с удалением volumes

```bash
docker-compose down -v
```

### Полная очистка (включая образы)

```bash
docker-compose down -v --rmi all
```

## Production Deployment

### Рекомендации для production

1. **Используйте docker-compose.prod.yml**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Настройте логирование**
   ```yaml
   logging:
     driver: "json-file"
     options:
       max-size: "10m"
       max-file: "3"
   ```

3. **Добавьте resource limits**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '1'
         memory: 2G
   ```

4. **Используйте secrets для конфиденциальных данных**

5. **Настройте reverse proxy (nginx/traefik)**

6. **Используйте Docker Swarm или Kubernetes для оркестрации**

## Дополнительная документация

- [Stock Interactor Docker](./stock-interactor/DOCKER.md)
- [Trade Engine Docker](./trade-engine/DOCKER.md)

## Поддержка

Для получения помощи создайте issue в репозитории проекта.

