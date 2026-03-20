# Stock Interactor

Trading bot application for cryptocurrency markets (Binance).

## Features

- Real-time WebSocket data streaming (klines, book ticker)
- Automatic reconnection with exponential backoff
- Graceful shutdown handling
- gRPC API for external control
- Configurable timeouts and retry strategies

## Quick Start

```bash
# Build
make build

# Run
./stock-interactor

# With custom config
READ_TIMEOUT=3s INIT_TIMEOUT=15s ./stock-interactor
```

## Configuration

Key environment variables:

- `READ_TIMEOUT` - Timeout for reading data from streams (default: 5s)
- `INIT_TIMEOUT` - Timeout for WebSocket initialization (default: 10s)
- `MAX_BACKOFF` - Maximum backoff for reconnection retries (default: 8s)
- `GRPC_SERVER_ADDR` - gRPC server address (required)
- `GRPC_CLIENT_ADDR` - gRPC client address (required)

See `internal/config/env.go` for full list.

## Architecture

```
cmd/main.go                 - Application entry point
internal/
  ├── application/          - Application orchestration
  ├── candle_worker/        - Kline data processing
  ├── spread_worker/        - Book ticker processing
  ├── receiver_worker/      - Decision making
  ├── api/                  - gRPC API
  ├── transport/            - External API communication
  └── usecases/             - Business logic
pkg/
  └── stream/               - WebSocket utilities
```

## Documentation

📚 **[Full Documentation](./docs/README.md)**

### Notable Docs:
- [Graceful Shutdown Race Condition](./docs/debugging/graceful-shutdown-race-condition.md) - Deep dive into a complex production bug
- [War Stories](./docs/WAR_STORIES.md) - Collection of interesting problems solved
- [Code Review Checklist](./docs/CODE_REVIEW_CHECKLIST.md) - Best practices derived from real bugs

## Development

```bash
# Run tests
go test ./...

# Run with race detector
go test -race ./...

# Profile with pprof
# (pprof server runs on :6060 when app is running)
go tool pprof http://localhost:6060/debug/pprof/goroutine
```

## Debugging

Application includes built-in debugging tools:

- **pprof server**: `http://localhost:6060/debug/pprof/`
- **Goroutine dump**: Automatically triggered if shutdown takes > 10 seconds
- **Structured logging**: All operations logged with context

## Production Notes

- All network operations have configurable timeouts
- Graceful shutdown tested under various timing conditions
- Automatic reconnection with exponential backoff
- Non-blocking error reporting during shutdown

For operational details, see [docs/](./docs/).

## License

[Your License Here]

---

**Last Updated:** 2025-12-22
