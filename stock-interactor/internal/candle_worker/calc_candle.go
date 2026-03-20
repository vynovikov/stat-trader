package candleworker

import (
	"fmt"
	"strconv"

	"github.com/vector-trader/stock-interactor/internal/entities"
)

func calcCandle(candle entities.Candle, price string, qty string) (entities.Candle, error) {
	priceFloat, err := strconv.ParseFloat(price, 64)
	if err != nil {
		return candle, fmt.Errorf("priceFloat %v", err)
	}

	qtyFloat, err := strconv.ParseFloat(qty, 64)
	if err != nil {
		return candle, fmt.Errorf("qtyFloat %v", err)
	}

	candle.Close = priceFloat

	if priceFloat > candle.High {
		candle.High = priceFloat
	}
	if priceFloat < candle.Low {
		candle.Low = priceFloat
	}

	candle.Volume += qtyFloat

	return candle, nil
}
