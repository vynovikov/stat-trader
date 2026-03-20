package transport

import (
	"strconv"
	"time"

	emperror "emperror.dev/errors"
	"github.com/adshao/go-binance/v2/futures"
	"github.com/vector-trader/stock-interactor/internal/entities"
	"github.com/vector-trader/stock-interactor/internal/pb"
)

func unmarshalDecision(response *pb.DecideResponse) entities.Decision {
	return entities.Decision{
		MarketAction: entities.MarketAction(response.GetMarketAction()),
		Order: entities.Order{
			CandleAction: entities.CandleAction(response.GetOrder().GetCandleAction()),
			Entry:        response.GetOrder().GetEntry(),
			SL:           response.GetOrder().GetSl(),
			TP:           response.GetOrder().GetTp(),
			Volume:       response.GetOrder().GetVolume(),
		},
	}
}

func unmarshalKlines(raw []*futures.Kline, symbol string) ([]entities.Candle, error) {
	candles := make([]entities.Candle, len(raw))
	for i, r := range raw {
		openTime := time.UnixMilli(r.OpenTime)
		closeTime := time.UnixMilli(r.CloseTime)

		open, err := strconv.ParseFloat(r.Open, 64)
		if err != nil {
			return nil, emperror.Wrap(err, "transport.IntervalCandles parseFloat open")
		}

		high, err := strconv.ParseFloat(r.High, 64)
		if err != nil {
			return nil, emperror.Wrap(err, "transport.IntervalCandles parseFloat high")
		}

		low, err := strconv.ParseFloat(r.Low, 64)
		if err != nil {
			return nil, emperror.Wrap(err, "transport.IntervalCandles parseFloat low")
		}

		close, err := strconv.ParseFloat(r.Close, 64)
		if err != nil {
			return nil, emperror.Wrap(err, "transport.IntervalCandles parseFloat close")
		}

		candles[i] = entities.Candle{
			Symbol:    symbol,
			OpenTime:  openTime,
			CloseTime: closeTime,

			Open:  open,
			High:  high,
			Low:   low,
			Close: close,
		}
	}
	return candles, nil
}
