package usecases

import (
	"context"

	"github.com/vector-trader/stock-interactor/internal/entities"
)

func (d *domainStruct) IntervalCandles(
	ctx context.Context,
	symbol string,
	interval string,
	fromTimestamp int64,
	toTimestamp int64,
) ([]entities.Candle, error) {

	return d.transport.IntervalCandles(ctx, symbol, interval, fromTimestamp, toTimestamp)
}
