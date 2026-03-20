package ticker

import (
	"context"
	"log/slog"
	"sync"
	"time"

	"github.com/vector-trader/stock-interactor/internal/cache"
	candleWorker "github.com/vector-trader/stock-interactor/internal/candle_worker"
	"github.com/vector-trader/stock-interactor/internal/entities"
	metricsPkg "github.com/vector-trader/stock-interactor/internal/metrics"
	priceWorker "github.com/vector-trader/stock-interactor/internal/price_worker"
	receiverWorker "github.com/vector-trader/stock-interactor/internal/receiver_worker"
	spreadWorker "github.com/vector-trader/stock-interactor/internal/spread_worker"
	"github.com/vector-trader/stock-interactor/internal/stream"
	streamInfo "github.com/vector-trader/stock-interactor/internal/stream_info"
)

type RealtimeTicker struct {
	candleStreamInfo streamInfo.StreamInfo
	candleStream     stream.Stream

	priceStreamInfo streamInfo.StreamInfo
	priceStream     stream.Stream

	bookStreamInfo streamInfo.StreamInfo
	bookStream     stream.Stream

	symbol string
	domain domain

	maxBackoff  time.Duration
	readTimeout time.Duration
	initTimeout time.Duration

	metricsCollector metricsPkg.MetricsCollector

	logger *slog.Logger
}

func NewRealtimeTicker(
	candleStreamInfo streamInfo.StreamInfo,
	priceStreamInfo streamInfo.StreamInfo,
	bookStreamInfo streamInfo.StreamInfo,
	symbol string,
	domain domain,
	chanErr chan error,
	maxBackoff time.Duration,
	readTimeout time.Duration,
	initTimeout time.Duration,
	metricsCollector metricsPkg.MetricsCollector,
	logger *slog.Logger,
) (RealtimeTicker, chan entities.Candle, chan float64, error) {
	var (
		candleStream stream.Stream
		priceStream  stream.Stream
		bookStream   stream.Stream
		wg           sync.WaitGroup
	)
	chanStream := make(chan stream.Stream, 3)

	ctxInit, cancel := context.WithTimeout(context.Background(), time.Second*2)
	defer cancel()

	wg.Add(3)
	go stream.InitStreamConcurrent(
		ctxInit,
		&wg,
		chanStream,
		chanErr,
		candleStreamInfo.URL(),
		candleStreamInfo.Name(),
		candleStreamInfo.Method(),
		candleStreamInfo.ID(),
		initTimeout,
		logger,
	)
	go stream.InitStreamConcurrent(
		ctxInit,
		&wg,
		chanStream,
		chanErr,
		priceStreamInfo.URL(),
		priceStreamInfo.Name(),
		priceStreamInfo.Method(),
		priceStreamInfo.ID(),
		initTimeout,
		logger,
	)
	go stream.InitStreamConcurrent(
		ctxInit,
		&wg,
		chanStream,
		chanErr,
		bookStreamInfo.URL(),
		bookStreamInfo.Name(),
		bookStreamInfo.Method(),
		bookStreamInfo.ID(),
		initTimeout,
		logger,
	)
	wg.Wait()

	close(chanStream)

	for stream := range chanStream {
		switch stream.ID() {
		case streamInfo.StreamCandle:
			candleStream = stream
		case streamInfo.StreamPrice:
			priceStream = stream
		case streamInfo.StreamBook:
			bookStream = stream
		}
	}

	return RealtimeTicker{
		candleStreamInfo: candleStreamInfo,
		candleStream:     candleStream,
		priceStreamInfo:  priceStreamInfo,
		priceStream:      priceStream,
		bookStreamInfo:   bookStreamInfo,
		bookStream:       bookStream,
		domain:           domain,
		symbol:           symbol,
		maxBackoff:       maxBackoff,
		readTimeout:      readTimeout,
		initTimeout:      initTimeout,
		metricsCollector: metricsCollector,
		logger:           logger,
	}, make(chan entities.Candle, 10), make(chan float64, 10), nil
}

func (t RealtimeTicker) Run(
	ctx context.Context,
	cache cache.Cache,
	chanCandle chan entities.Candle,
	chanTime chan time.Duration,
	chanSpread chan float64,
	chanErr chan error,
) {
	wg := sync.WaitGroup{}

	candleWorker, err := candleWorker.NewCandleWorker(
		t.candleStreamInfo,
		t.candleStream,
		cache,
		t.domain,
		t.maxBackoff,
		t.readTimeout,
		t.initTimeout,
		t.metricsCollector,
		t.logger,
	)
	if err != nil {
		chanErr <- err
		return
	}

	priceWorker := priceWorker.NewPriceWorker(
		t.priceStreamInfo,
		t.priceStream,
		cache,
		time.Second,
		time.Second,
		t.logger,
	)

	spreadWorker, err := spreadWorker.NewSpreadWorker(
		t.bookStreamInfo,
		t.bookStream,
		cache,
		t.maxBackoff,
		t.readTimeout,
		t.initTimeout,
		t.logger,
	)
	if err != nil {
		chanErr <- err
		return
	}

	receiverWorker := receiverWorker.NewReceiverWorker(
		cache,
		t.domain,
	)

	wg.Add(4)
	go candleWorker.Work(ctx, &wg, t.symbol, chanCandle, chanTime, chanErr)
	go priceWorker.Work(ctx, &wg, chanTime, chanErr)
	go spreadWorker.Work(ctx, &wg, chanSpread, chanErr)
	go receiverWorker.Work(ctx, &wg, t.symbol, chanCandle, chanErr)
	wg.Wait()
}
