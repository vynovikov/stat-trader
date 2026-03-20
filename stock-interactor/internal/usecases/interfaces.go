package usecases

import (
	"context"

	"github.com/vector-trader/stock-interactor/internal/entities"
)

type transport interface {
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

	Decide(
		ctx context.Context,
		candle entities.Candle,
		spread float64,
		balance float64,
	) (entities.Decision, error)

	OpenOrder(
		ctx context.Context,
		symbol string,
		order entities.Order,
	) error

	CloseOrder(
		ctx context.Context,
		symbol string,
	) error

	SetLimitSL(
		ctx context.Context,
		symbol string,
		order entities.Order,
		limitSLTrigger string,
		limitSLPrice string,
	) error

	SetMarketSL(
		ctx context.Context,
		symbol string,
		order entities.Order,
		marketSL string,
	) error

	SetLimitTP(
		ctx context.Context,
		symbol string,
		order entities.Order,
		limitTPTrigger string,
		limitTPPrice string,
	) error

	SetMarketTP(
		ctx context.Context,
		symbol string,
		order entities.Order,
		marketTP string,
	) error

	Balance(
		ctx context.Context,
		symbol string,
	) (float64, error)
}
