package candleworker

import (
	"log/slog"
	"time"

	metricsPkg "github.com/vector-trader/stock-interactor/internal/metrics"

	"github.com/vector-trader/stock-interactor/internal/cache"
	readCloser "github.com/vector-trader/stock-interactor/internal/read_closer"
	"github.com/vector-trader/stock-interactor/internal/stream"
	streamInfo "github.com/vector-trader/stock-interactor/internal/stream_info"
)

type candleWorker struct {
	candleStreamInfo streamInfo.StreamInfo
	candleReader     readCloser.Reader
	cache            cache.Cache
	domain           domain
	stopIn           *time.Timer
	startIn          *time.Timer
	maxBackoff       time.Duration
	readTimeout      time.Duration
	initTimeout      time.Duration
	metricsCollector metricsPkg.MetricsCollector
	logger           *slog.Logger
}

func NewCandleWorker(
	candleStreamInfo streamInfo.StreamInfo,
	candleStream stream.Stream,
	cache cache.Cache,
	domain domain,
	maxBackoff time.Duration,
	readTimeout time.Duration,
	initTimeout time.Duration,
	metricsCollector metricsPkg.MetricsCollector,
	logger *slog.Logger,
) (*candleWorker, error) {
	candleReader := readCloser.NewWSReader(candleStream.Conn(), readTimeout)

	return &candleWorker{
		candleStreamInfo: candleStreamInfo,
		candleReader:     candleReader,
		cache:            cache,
		domain:           domain,
		stopIn:           &time.Timer{},
		startIn:          time.NewTimer(0),
		maxBackoff:       maxBackoff,
		readTimeout:      readTimeout,
		initTimeout:      initTimeout,
		metricsCollector: metricsCollector,
		logger:           logger,
	}, nil
}
