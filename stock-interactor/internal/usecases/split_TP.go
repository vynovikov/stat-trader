package usecases

import (
	"log"
	"strconv"

	"github.com/vector-trader/stock-interactor/internal/entities"
)

func (d *domainStruct) splitTP(order entities.Order) (string, string, string) {
	limitTPPrice := order.TP
	var (
		limitTPTrigger float64
		marketTP       float64
	)

	switch order.CandleAction {
	case entities.CandleActionBuy:
		limitTPTrigger = limitTPPrice - 10*d.minPriceDelta
		marketTP = limitTPPrice + 10*d.minPriceDelta

	case entities.CandleActionSell:
		limitTPTrigger = limitTPPrice + 10*d.minPriceDelta
		marketTP = limitTPPrice - 10*d.minPriceDelta
	}

	limitTPTriggerString := strconv.FormatFloat(limitTPTrigger, 'f', 0, 64)
	limitTPPriceString := strconv.FormatFloat(limitTPPrice, 'f', 0, 64)
	marketTPString := strconv.FormatFloat(marketTP, 'f', 0, 64)

	log.Printf("limitTPPrice %.0f, limitTPTrigger %.0f marketTP %.0f", limitTPPrice, limitTPTrigger, marketTP)

	return limitTPTriggerString, limitTPPriceString, marketTPString
}
