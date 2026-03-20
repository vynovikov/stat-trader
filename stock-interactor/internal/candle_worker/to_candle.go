package candleworker

import (
	"strconv"
	"time"

	"github.com/vector-trader/stock-interactor/internal/entities"
)

func toCandle(k klineObj) (entities.Candle, error) {
	openTime := time.UnixMilli(k.OpenTime)
	closeTime := time.UnixMilli(k.CloseTime)

	open, err := strconv.ParseFloat(k.Open, 64)
	if err != nil {
		return entities.Candle{}, err
	}

	high, err := strconv.ParseFloat(k.High, 64)
	if err != nil {
		return entities.Candle{}, err
	}

	low, err := strconv.ParseFloat(k.Low, 64)
	if err != nil {
		return entities.Candle{}, err
	}

	close, err := strconv.ParseFloat(k.Close, 64)
	if err != nil {
		return entities.Candle{}, err
	}

	volume, err := strconv.ParseFloat(k.Volume, 64)
	if err != nil {
		return entities.Candle{}, err
	}

	return entities.Candle{
		Symbol:    k.Symbol,
		Interval:  k.Interval,
		OpenTime:  openTime,
		CloseTime: closeTime,
		Open:      open,
		High:      high,
		Low:       low,
		Close:     close,
		Volume:    volume,
	}, nil
}
