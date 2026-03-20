package usecases

import (
	"log/slog"

	"github.com/vector-trader/stock-interactor/internal/cache"
)

type domainStruct struct {
	cache         cache.Cache
	transport     transport
	minPriceDelta float64
	chanErr       chan error
	logger        *slog.Logger
}

func New(
	cache cache.Cache,
	transport transport,
	minPriceDelta float64,
	chanErr chan error,
	logger *slog.Logger,
) *domainStruct {
	return &domainStruct{
		cache:         cache,
		transport:     transport,
		minPriceDelta: minPriceDelta,
		chanErr:       chanErr,
		logger:        logger,
	}
}
