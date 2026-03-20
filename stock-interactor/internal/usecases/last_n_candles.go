package usecases

import (
	"context"

	"github.com/vector-trader/stock-interactor/internal/entities"
)

func (d *domainStruct) LastNCandles(ctx context.Context, symbol string, interval string, limit int) ([]entities.Candle, error) {
	return d.transport.LastNCandles(ctx, symbol, interval, limit)
}
