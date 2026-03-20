package cache

import "github.com/vector-trader/stock-interactor/internal/entities"

type Cache interface {
	Balance() float64
	SetBalance(Balance float64)
	Price() float64
	SetPrice(Balance float64)
	Spread() float64
	SetSpread(spread float64)
	Candle() entities.Candle
	SetCandle(candle entities.Candle)
}
