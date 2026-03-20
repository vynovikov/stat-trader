package usecases

import (
	"math"

	"github.com/vector-trader/stock-interactor/internal/entities"
)

func (d *domainStruct) getOrder(initial entities.Decision) entities.Order {
	return entities.Order{
		CandleAction: initial.Order.CandleAction,
		Entry:        math.Round(initial.Order.Entry*10) / 10,
		SL:           math.Round(initial.Order.SL*10) / 10,
		TP:           math.Round(initial.Order.TP*10) / 10,
		Volume:       math.Round(initial.Order.Volume*1000) / 1000,
	}
}
