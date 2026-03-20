# 🚀 Quick Start Guide - Vector Trader

## ✅ Что готово

Вся система Vector Trader контейнеризирована и готова к запуску в Docker!

### Созданные Docker образы

| Сервис | Размер | Описание |
|--------|--------|----------|
| **stock-interactor** | 23.4 MB | Go-сервис для работы с Binance API |
| **trade-engine** | 926 MB | Python ML-сервис с торговыми стратегиями |
| **qdrant** | ~400 MB | Векторная база данных (официальный образ) |

## 🏗️ Архитектура

```
Internet
   │
   └─► Binance API
           │
           ▼
    ┌──────────────────┐
    │ stock-interactor │ :5001
    │   (Go, 23 MB)    │
    └────────┬─────────┘
             │ gRPC
             ▼
    ┌──────────────────┐     ┌──────────┐
    │  trade-engine    │────►│  Qdrant  │
    │ (Python, 926 MB) │     │  :6333   │
    │      :5002       │     │  :6334   │
    └──────────────────┘     └──────────┘
```

## 🚀 Быстрый запуск

### 1️⃣ Запуск всех сервисов

```bash
# Из корня проекта vector-trader
docker compose up -d
```

### 2️⃣ Проверка статуса

```bash
docker compose ps
```

Ожидаемый результат:
```
NAME                  STATUS        PORTS
qdrant_vector_db     Up (healthy)  0.0.0.0:6333-6334->6333-6334/tcp
stock_interactor     Up (healthy)  0.0.0.0:5001->5001/tcp, 0.0.0.0:6060->6060/tcp
trade_engine         Up (healthy)  0.0.0.0:5002->5002/tcp
```

### 3️⃣ Просмотр логов

```bash
# Все сервисы
docker compose logs -f

# Конкретный сервис
docker compose logs -f stock-interactor
docker compose logs -f trade-engine
```

### 4️⃣ Остановка

```bash
docker compose down
```

## 🔧 Настройка

### Переменные окружения

1. Скопируйте пример конфигурации:
```bash
cp config.env.example .env
```

2. Отредактируйте `.env` под ваши нужды:
```bash
nano .env
```

3. Перезапустите с новой конфигурацией:
```bash
docker compose up -d
```

### Основные параметры

```env
# Торговая пара
SYMBOL=BTCUSDT

# Таймфрейм
TIMEFRAME=5m

# Лимит свечей от Binance
BINANCE_CANDLES_LIMIT=1000
```

## 🧪 Проверка работоспособности

### Stock Interactor (Go)

```bash
# Проверка gRPC
grpcurl -plaintext localhost:5001 list

# Проверка pprof (профилирование)
curl http://localhost:6060/debug/pprof/
```

### Trade Engine (Python)

```bash
# Проверка gRPC
grpcurl -plaintext localhost:5002 list

# Проверка логов
docker logs trade_engine
```

### Qdrant (Vector DB)

```bash
# Проверка health
curl http://localhost:6333/health

# REST API
curl http://localhost:6333/collections
```

## 📊 Мониторинг

### Использование ресурсов

```bash
docker stats stock_interactor trade_engine qdrant_vector_db
```

### Health статус

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

## 🐛 Troubleshooting

### Проблема: Сервисы не запускаются

**Проверьте порты:**
```bash
# Убедитесь, что порты 5001, 5002, 6333, 6334 свободны
sudo lsof -i :5001
sudo lsof -i :5002
sudo lsof -i :6333
```

**Проверьте логи:**
```bash
docker compose logs
```

### Проблема: trade-engine не может подключиться к stock-interactor

**Решение:** Убедитесь, что stock-interactor здоров:
```bash
docker ps
# Проверьте колонку STATUS - должно быть "Up (healthy)"
```

### Проблема: Qdrant не может создать директорию

**Решение:** Создайте директории с правильными правами:
```bash
mkdir -p trade-engine/qdrant/data
mkdir -p trade-engine/qdrant/config
sudo chown -R 1000:1000 trade-engine/qdrant/
```

## 🔄 Обновление

### Пересборка после изменений

```bash
# Пересобрать все
docker compose build

# Пересобрать конкретный сервис
docker compose build stock-interactor
docker compose build trade-engine

# Запуск с пересборкой
docker compose up -d --build
```

## 📁 Структура проекта

```
vector-trader/
├── docker-compose.yml          # Главный compose файл
├── config.env.example          # Пример конфигурации
├── DOCKER_README.md            # Подробная документация
├── QUICKSTART.md               # Этот файл
│
├── stock-interactor/
│   ├── Dockerfile              # Двухуровневая сборка Go
│   ├── .dockerignore           # Исключения для Docker
│   └── DOCKER.md               # Документация по stock-interactor
│
└── trade-engine/
    ├── Dockerfile              # Двухуровневая сборка Python
    ├── .dockerignore           # Исключения для Docker
    ├── DOCKER.md               # Документация по trade-engine
    └── docker-compose.yml      # Старый compose (для справки)
```

## 📚 Дополнительная документация

- [Полная Docker документация](./DOCKER_README.md)
- [Stock Interactor](./stock-interactor/DOCKER.md)
- [Trade Engine](./trade-engine/DOCKER.md)

## 🎯 Следующие шаги

1. ✅ Запустите систему: `docker compose up -d`
2. ✅ Проверьте логи: `docker compose logs -f`
3. ✅ Настройте мониторинг: `docker stats`
4. 🔜 Интеграция с вашим торговым ботом
5. 🔜 Настройка production окружения

## 💡 Полезные команды

```bash
# Полная очистка (включая volumes)
docker compose down -v

# Просмотр сети
docker network inspect vector-trader-network

# Запуск конкретного сервиса
docker compose up -d stock-interactor

# Перезапуск сервиса
docker compose restart trade-engine

# Интерактивный shell
docker exec -it stock_interactor sh
docker exec -it trade_engine bash
```

---

**🎉 Готово! Ваша система Vector Trader запущена в Docker!**

