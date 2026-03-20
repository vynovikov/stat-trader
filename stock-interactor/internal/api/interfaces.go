package api

import (
	"context"

	"github.com/vector-trader/stock-interactor/internal/entities"
)

type domain interface {
	LastNCandles(
		ctx context.Context,
		symbol string,
		interval string,
		limit int,
	) ([]entities.Candle, error)

	IntervalCandles(
		ctx context.Context,
		symbol string,
		interval string,
		fromTimestamp int64,
		toTimestamp int64,
	) ([]entities.Candle, error)

	OpenOrder(
		ctx context.Context,
		symbol string,
		order entities.Order,
	) error

	CloseOrder(
		ctx context.Context,
		symbol string,
	) (float64, error)
}
