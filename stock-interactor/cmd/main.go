package main

import (
	"context"
	"fmt"
	"log/slog"
	"net/http"
	_ "net/http/pprof"
	"os"
	"os/signal"
	"runtime"
	"runtime/pprof"
	"syscall"
	"time"

	"github.com/vector-trader/stock-interactor/internal/application"
	"github.com/vector-trader/stock-interactor/internal/config"
	pkgLogger "github.com/vector-trader/stock-interactor/pkg/logger"
)

func main() {
	ctx, cancel := signal.NotifyContext(
		context.Background(),
		syscall.SIGINT,
		syscall.SIGTERM,
	)
	defer cancel()
	logger := slog.New(pkgLogger.NewPrettyHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelDebug,
	}))

	cfg, err := config.Parse()
	if err != nil {
		logger.ErrorContext(ctx, fmt.Sprintf("failed to parse config: %v", err))

		return
	}

	runtime.SetBlockProfileRate(1)
	runtime.SetMutexProfileFraction(1)

	go func() {
		addr := "127.0.0.1:6060"
		srv := &http.Server{
			Addr:              addr,
			ReadHeaderTimeout: 5 * time.Second,
		}
		// Закрытие сервера на shutdown
		go func() {
			<-ctx.Done()
			shutdownCtx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
			defer cancel()
			_ = srv.Shutdown(shutdownCtx)
		}()
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Error("pprof server error", "err", err)
		}
	}()

	go func() {
		<-ctx.Done()

		// Если через 10 секунд не завершились — печатаем все горутины.
		t := time.NewTimer(10 * time.Second)
		defer t.Stop()

		<-t.C
		logger.Error("shutdown seems stuck; dumping goroutines")
		_ = pprof.Lookup("goroutine").WriteTo(os.Stderr, 2)
	}()

	err = application.Start(ctx, cancel, cfg, logger)
	if err != nil {
		logger.ErrorContext(ctx, fmt.Sprintf("failed to start application: %v", err))

		return
	}
}
