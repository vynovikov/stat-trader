package transport

import (
	"context"
	"time"

	emperror "emperror.dev/errors"
	"github.com/vector-trader/stock-interactor/internal/entities"
)

func (t transportStruct) IntervalCandles(
	ctx context.Context,
	symbol string,
	interval string,
	fromTimestamp int64,
	toTimestamp int64,
) ([]entities.Candle, error) {
	start := time.Unix(fromTimestamp, 0)
	end := time.Unix(toTimestamp, 0)

	total := int(time.Duration(end.Sub(start)) / time.Duration(5*time.Minute))

	result := make([]entities.Candle, 0, total)

	for start.Before(end) {
		raw, err := t.stockClient.NewKlinesService().
			Symbol(symbol).
			Interval(interval).
			StartTime(start.UnixMilli()).
			EndTime(end.UnixMilli()).
			Limit(MAX_CANDLES_PER_REQUEST).
			Do(ctx)
		if err != nil {
			return nil, emperror.Wrap(err, "transport.IntervalCandles")
		}

		if len(raw) == 0 {
			break
		}

		candles, err := unmarshalKlines(raw, symbol)
		if err != nil {
			return nil, emperror.Wrap(err, "transport.IntervalCandles unmarshalKlines")
		}

		result = append(result, candles...)

		lastCandle := raw[len(raw)-1]
		start = time.UnixMilli(lastCandle.CloseTime + 1)
	}

	return result, nil
}
