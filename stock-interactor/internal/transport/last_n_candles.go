package transport

import (
	"context"

	emperror "emperror.dev/errors"
	"github.com/vector-trader/stock-interactor/internal/entities"
)

func (t transportStruct) LastNCandles(ctx context.Context, symbol string, interval string, limit int) ([]entities.Candle, error) {
	ctx, cancel := context.WithTimeout(ctx, t.requestTimeout)
	defer cancel()

	raw, err := t.stockClient.NewKlinesService().
		Symbol(symbol).
		Interval(interval).
		Limit(limit + 1).
		Do(ctx)
	if err != nil {
		return nil, emperror.Wrap(err, "transport.LastNCandles")
	}

	result, err := unmarshalKlines(raw, symbol)
	if err != nil {
		return nil, emperror.Wrap(err, "transport.LastNCandles")
	}

	return result[:len(result)-1], nil // only closed ones
}
