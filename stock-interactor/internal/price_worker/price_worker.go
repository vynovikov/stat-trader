package priceworker

import (
	"log/slog"
	"time"

	"github.com/vector-trader/stock-interactor/internal/cache"
	readCloser "github.com/vector-trader/stock-interactor/internal/read_closer"
	"github.com/vector-trader/stock-interactor/internal/stream"
	streamInfo "github.com/vector-trader/stock-interactor/internal/stream_info"
)

type priceWorker struct {
	priceStreamInfo streamInfo.StreamInfo
	priceReader     readCloser.Reader
	cache           cache.Cache
	stopTimer       *time.Timer
	waitTimer       *time.Timer
	initTimeout     time.Duration
	readTimeout     time.Duration
	logger          *slog.Logger
}

func NewPriceWorker(
	priceStreamInfo streamInfo.StreamInfo,
	priceStream stream.Stream,
	cache cache.Cache,
	initTimeout time.Duration,
	readTimeout time.Duration,
	logger *slog.Logger,
) *priceWorker {
	priceReader := readCloser.NewWSReader(priceStream.Conn(), readTimeout)

	return &priceWorker{
		priceStreamInfo: priceStreamInfo,
		priceReader:     priceReader,
		cache:           cache,
		stopTimer:       time.NewTimer(0),
		waitTimer:       &time.Timer{},
		initTimeout:     initTimeout,
		readTimeout:     readTimeout,
		logger:          logger,
	}
}
