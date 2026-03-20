ARG TARGETOS=linux
ARG TARGETARCH

# Stage 1: Builder
# Используем нативную платформу хоста для быстрой компиляции
FROM --platform=$BUILDPLATFORM golang:1.24rc2-alpine AS builder

# Установка необходимых инструментов для сборки
RUN apk add --no-cache git make ca-certificates

# Установка рабочей директории
WORKDIR /build

# Копирование go.mod и go.sum для кэширования зависимостей
COPY go.mod go.sum ./

# Загрузка и установка нужного toolchain, затем загрузка зависимостей
RUN go install golang.org/dl/go1.24.11@latest && \
    /go/bin/go1.24.11 download && \
    /go/bin/go1.24.11 mod download && \
    /go/bin/go1.24.11 mod verify

# Копирование всего исходного кода
COPY . .

# Обновляем go.mod для новой версии Go
RUN /go/bin/go1.24.11 mod tidy

# Получаем значения TARGETARCH и TARGETOS для кросс-компиляции
ARG TARGETOS
ARG TARGETARCH

# Сборка приложения с оптимизацией размера
# Компилируем на нативной платформе хоста, но для целевой архитектуры
# Go поддерживает кросс-компиляцию без эмуляции!
RUN CGO_ENABLED=0 GOOS=${TARGETOS} GOARCH=${TARGETARCH} \
    /go/bin/go1.24.11 build \
    -ldflags="-s -w" \
    -o stock-interactor \
    ./cmd/main.go

# Stage 2: Runtime
# Этот stage использует целевую платформу (arm64 или amd64)
FROM alpine:latest

# Установка CA-сертификатов для HTTPS запросов и timezone data
RUN apk --no-cache add ca-certificates tzdata

# Создание непривилегированного пользователя
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser

# Установка рабочей директории
WORKDIR /app

# Копирование бинарника из builder stage
COPY --from=builder --chown=appuser:appuser /build/stock-interactor .

# Переключение на непривилегированного пользователя
USER appuser

# Expose порт gRPC сервера
EXPOSE 5000

# Expose порт pprof (опционально, для отладки)
EXPOSE 6060

# Команда запуска
ENTRYPOINT ["./stock-interactor"]