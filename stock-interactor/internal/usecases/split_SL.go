package usecases

import (
	"strconv"

	"github.com/vector-trader/stock-interactor/internal/entities"
)

func (d *domainStruct) splitSL(order entities.Order) (string, string, string) {
	limitSLPrice := order.SL
	var (
		limitSLTrigger float64
		marketSL       float64
	)

	switch order.CandleAction {

	case entities.CandleActionBuy:
		limitSLTrigger = limitSLPrice + 10*d.minPriceDelta
		marketSL = limitSLPrice - 10*d.minPriceDelta

	case entities.CandleActionSell:
		limitSLTrigger = limitSLPrice - 10*d.minPriceDelta
		marketSL = limitSLPrice + 10*d.minPriceDelta
	}

	limitSLPriceString := strconv.FormatFloat(limitSLPrice, 'f', 0, 64)
	limitSLTriggerString := strconv.FormatFloat(limitSLTrigger, 'f', 0, 64)
	marketSLString := strconv.FormatFloat(marketSL, 'f', 0, 64)

	return limitSLTriggerString, limitSLPriceString, marketSLString
}
