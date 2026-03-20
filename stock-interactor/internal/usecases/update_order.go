package usecases

import (
	"log"

	"github.com/vector-trader/stock-interactor/internal/entities"
)

func (d *domainStruct) updateOrder(initialOrder entities.Order, candle entities.Candle, lastPrice float64) entities.Order {
	difference := lastPrice - candle.Close

	entry := initialOrder.Entry + difference

	log.Printf("[usecases.updateOrder] entry %.0f, difference %.0f, updated_entry %.0f", initialOrder.Entry, difference, entry)

	return entities.Order{
		CandleAction: initialOrder.CandleAction,
		Entry:        entry,
		SL:           initialOrder.SL,
		TP:           initialOrder.TP,
		Volume:       initialOrder.Volume,
	}
}
