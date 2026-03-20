package application

import (
	"context"
	"fmt"
	"log"
	"log/slog"
	"net/http"
	"sync"
	"time"

	emperror "emperror.dev/errors"

	"github.com/prometheus/client_golang/prometheus/promhttp"
	apiPkg "github.com/vector-trader/stock-interactor/internal/api"
	"github.com/vector-trader/stock-interactor/internal/cache"
	"github.com/vector-trader/stock-interactor/internal/config"
	metricsPkg "github.com/vector-trader/stock-interactor/internal/metrics"
	streamInfo "github.com/vector-trader/stock-interactor/internal/stream_info"
	"github.com/vector-trader/stock-interactor/internal/ticker"
	transportPkg "github.com/vector-trader/stock-interactor/internal/transport"
	usecasesPkg "github.com/vector-trader/stock-interactor/internal/usecases"
)

func Start(ctx context.Context, cancel context.CancelFunc, cfg config.ENV, logger *slog.Logger) error {
	var wg sync.WaitGroup
	cache := cache.New()
	chanTime := make(chan time.Duration, 1)
	chanErr := make(chan error, 1)

	metricsCollector := metricsPkg.NewMetricsCollector()

	metricsMux := http.NewServeMux()
	metricsMux.Handle("/metrics", promhttp.Handler())

	maxBackoff, err := time.ParseDuration(cfg.MaxBackoff)
	if err != nil {
		return emperror.Wrapf(err, "application.Start")
	}

	readTimeout, err := time.ParseDuration(cfg.ReadTimeout)
	if err != nil {
		return emperror.Wrapf(err, "application.Start")
	}

	initTimeout, err := time.ParseDuration(cfg.InitTimeout)
	if err != nil {
		return emperror.Wrapf(err, "application.Start")
	}

	interactorTransport, err := transportPkg.New(ctx, cfg, logger)
	if err != nil {
		return emperror.Wrap(err, "application.Start")
	}

	interactorDomain := usecasesPkg.New(
		cache,
		interactorTransport,
		float64(cfg.MinPriceDelta),
		chanErr,
		logger,
	)
	interactorAPI := apiPkg.New(interactorDomain, cfg, logger)

	wg.Add(4)

	go func() {
		defer wg.Done()
		apiPkg.Run(ctx, interactorAPI, cfg, chanErr)
	}()

	log.Println(
		cfg.WSURLCandle,
		cfg.WSStreamNameCandle,
		cfg.WSMethodCandle,
	)

	candleStreamInfo := streamInfo.NewStreamInfo(
		cfg.WSURLCandle,
		cfg.WSStreamNameCandle,
		cfg.WSMethodCandle,
		streamInfo.StreamCandle,
	)

	priceStreamInfo := streamInfo.NewStreamInfo(
		cfg.WSURLPrice,
		cfg.WSStreamNamePrice,
		"",
		streamInfo.StreamPrice,
	)

	bookStreamInfo := streamInfo.NewStreamInfo(
		cfg.WSURLBook,
		cfg.WSStreamNameBook,
		"",
		streamInfo.StreamBook,
	)

	ticker, chanCandle, chanSpread, err := ticker.NewRealtimeTicker(
		candleStreamInfo,
		priceStreamInfo,
		bookStreamInfo,
		cfg.Symbol,
		interactorDomain,
		chanErr,
		maxBackoff,
		readTimeout,
		initTimeout,
		metricsCollector,
		logger,
	)

	go func() {
		defer wg.Done()
		ticker.Run(ctx, cache, chanCandle, chanTime, chanSpread, chanErr)
	}()

	go func() {
		defer wg.Done()

		for {
			select {
			case <-ctx.Done():
				return
			//case candle := <-chanCandle:
			//	logger.InfoContext(ctx, fmt.Sprintf("[application.Start] Candle: %+v", candle))
			case err := <-chanErr:
				if err != nil {
					logger.ErrorContext(ctx, fmt.Sprintf("Error: %v", err))
				}
			case <-chanSpread:
				// keep the channel drained
			}
		}

	}()

	go func() {
		defer wg.Done()
		metricsServer := &http.Server{
			Addr:              ":9090",
			Handler:           metricsMux,
			ReadHeaderTimeout: 5 * time.Second,
		}

		go func() {
			<-ctx.Done()
			shutdownCtx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
			defer cancel()
			_ = metricsServer.Shutdown(shutdownCtx)
		}()

		logger.Info("Starting Prometheus metrics server on :9090")
		if err := metricsServer.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Error("metrics server error", "err", err)
		}
	}()

	wg.Wait()

	return nil
}
