package api

import (
	"log/slog"

	"github.com/vector-trader/stock-interactor/internal/config"
	"github.com/vector-trader/stock-interactor/internal/pb"
)

type API struct {
	pb.UnimplementedStockServer
	domain domain
	logger *slog.Logger
}

func New(
	domain domain,
	cfg config.ENV,
	logger *slog.Logger,
) API {
	return API{
		domain: domain,
		logger: logger,
	}
}

var _ pb.StockServer = (*API)(nil)
