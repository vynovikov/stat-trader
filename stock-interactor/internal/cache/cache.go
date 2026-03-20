package cache

import (
	"sync"

	"github.com/vector-trader/stock-interactor/internal/entities"
)

type CacheStruct struct {
	mu      sync.Mutex
	candle  entities.Candle
	balance float64
	spread  float64
	price   float64
}

func New() *CacheStruct {
	return &CacheStruct{
		mu:      sync.Mutex{},
		candle:  entities.Candle{},
		balance: 0,
		spread:  0,
		price:   0,
	}
}
