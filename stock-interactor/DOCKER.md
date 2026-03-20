# Docker для Stock-Interactor

## Сборка образа

```bash
docker build -t stock-interactor:latest .
```

## Запуск контейнера

```bash
docker run -d \
  --name stock-interactor \
  -p 5001:5001 \
  -p 6060:6060 \
  -e BINANCE_CANDLES_LIMIT=1000 \
  -e TRANSPORT_SEMAPHORE_SIZE=4 \
  -e ADDRESS_GRPC=:5001 \
  stock-interactor:latest
```

## Переменные окружения

| Переменная | Описание | Значение по умолчанию |
|-----------|----------|----------------------|
| `BINANCE_CANDLES_LIMIT` | Лимит свечей для запросов к Binance | `1000` |
| `TRANSPORT_SEMAPHORE_SIZE` | Размер семафора для транспорта | `4` |
| `ADDRESS_GRPC` | Адрес gRPC сервера | `:5001` |

## Порты

- `5001` - gRPC сервер
- `6060` - pprof (профилирование, опционально)

## Особенности сборки

### Двухуровневая сборка (Multi-stage build)

**Stage 1: Builder**
- Базовый образ: `golang:1.24rc2-alpine`
- Установка Go 1.24.11 через `golang.org/dl`
- Компиляция с оптимизацией размера
- Статическая линковка (`CGO_ENABLED=0`)

**Stage 2: Runtime**
- Базовый образ: `alpine:latest` (~5MB)
- Только скомпилированный бинарник
- CA-сертификаты для HTTPS запросов
- Непривилегированный пользователь `appuser`

### Размер образа

Финальный образ: **~23MB**

### Безопасность

- ✅ Непривилегированный пользователь (UID/GID 1000)
- ✅ Минимальный базовый образ
- ✅ Только необходимые зависимости
- ✅ Статическая компиляция без CGO

## Отладка

### Просмотр логов

```bash
docker logs -f stock-interactor
```

### Доступ к pprof

```bash
# Если контейнер запущен с проброшенным портом 6060
curl http://localhost:6060/debug/pprof/
```

### Проверка здоровья

```bash
# Проверка, что gRPC сервер отвечает
grpcurl -plaintext localhost:5001 list
```

## Docker Compose

Для использования с docker-compose см. файл `docker-compose.yml` в корне проекта.

