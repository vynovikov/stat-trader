package candleworker

import (
	"context"

	"github.com/vector-trader/stock-interactor/internal/entities"
)

type domain interface {
	Decide(
		ctx context.Context,
		symbol string,
		candle entities.Candle,
		spread float64,
		balance float64,
	)

	Balance(
		ctx context.Context,
		symbol string,
	) (float64, error)
}
