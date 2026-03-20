package transport

import (
	"github.com/adshao/go-binance/v2/futures"
	"github.com/vector-trader/stock-interactor/internal/entities"
)

func side(candleAction entities.CandleAction) futures.SideType {
	switch candleAction {
	case entities.CandleActionBuy:
		return futures.SideTypeBuy
	case entities.CandleActionSell:
		return futures.SideTypeSell
	default:
		return futures.SideType("")
	}
}

func oppositeSide(candleAction entities.CandleAction) futures.SideType {
	switch candleAction {
	case entities.CandleActionBuy:
		return futures.SideTypeSell
	case entities.CandleActionSell:
		return futures.SideTypeBuy
	default:
		return futures.SideType("")
	}
}
