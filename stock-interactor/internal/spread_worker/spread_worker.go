package spreadworker

import (
	"log/slog"
	"time"

	"github.com/vector-trader/stock-interactor/internal/cache"
	readCloser "github.com/vector-trader/stock-interactor/internal/read_closer"
	"github.com/vector-trader/stock-interactor/internal/stream"
	streamInfo "github.com/vector-trader/stock-interactor/internal/stream_info"
)

type spreadWorker struct {
	bookStreamInfo streamInfo.StreamInfo
	bookReader     readCloser.Reader
	cache          cache.Cache
	maxBackoff     time.Duration
	readTimeout    time.Duration
	initTimeout    time.Duration
	logger         *slog.Logger
}

func NewSpreadWorker(
	bookStreamInfo streamInfo.StreamInfo,
	bookStream stream.Stream,
	cache cache.Cache,
	maxBackoff time.Duration,
	readTimeout time.Duration,
	initTimeout time.Duration,
	logger *slog.Logger,
) (*spreadWorker, error) {
	bookReader := readCloser.NewWSReader(bookStream.Conn(), readTimeout)

	return &spreadWorker{
		bookStreamInfo: bookStreamInfo,
		bookReader:     bookReader,
		cache:          cache,
		maxBackoff:     maxBackoff,
		readTimeout:    readTimeout,
		initTimeout:    initTimeout,
		logger:         logger,
	}, nil
}
