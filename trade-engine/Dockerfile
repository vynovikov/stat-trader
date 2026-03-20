ARG TARGETPLATFORM
ARG BUILDPLATFORM

# Stage 1: Builder
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# ⚡ Используем минимальный requirements для runtime
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# Копирование исходного кода для генерации protobuf
COPY proto/ ./proto/
COPY pb/ ./pb/

# Генерация protobuf
RUN python3 -m grpc_tools.protoc \
    -I proto \
    --python_out=pb \
    --pyi_out=pb \
    --grpc_python_out=pb \
    proto/vector_trader.proto && \
    sed -i 's/^import vector_trader_pb2/from . import vector_trader_pb2/' pb/vector_trader_pb2_grpc.py || true

# Stage 2: Runtime
FROM python:3.12-slim

RUN useradd -m -u 1000 -s /bin/bash appuser

WORKDIR /app

COPY --from=builder /install /usr/local
COPY --chown=appuser:appuser . .

RUN mkdir -p /app/data /app/models && \
    chown -R appuser:appuser /app

USER appuser

ENV PYTHONPATH=/app

EXPOSE 5002

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import grpc; channel = grpc.insecure_channel('localhost:5002'); channel.close()" || exit 1

CMD ["python", "-u", "services/grpc_server/grpc_server_multi_engine.py"]