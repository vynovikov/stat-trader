package transport

import (
	"context"

	emperror "emperror.dev/errors"
	"github.com/adshao/go-binance/v2/futures"
	"github.com/vector-trader/stock-interactor/internal/entities"
)

func (t transportStruct) SetMarketSL(
	ctx context.Context,
	symbol string,
	order entities.Order,
	marketSL string,
) error {
	side := oppositeSide(order.CandleAction)
	if side == "" {
		return emperror.New("transport.SetMarketSL: unknown candleAction")
	}

	//qty := strings.TrimRight(strings.TrimRight(strconv.FormatFloat(order.Volume, 'f', 3, 64), "0"), ".")

	if t.isTradingEnabled {
		_, err := t.stockClient.NewCreateAlgoOrderService().
			Symbol(symbol).
			Side(side).
			Type(futures.AlgoOrderTypeStopMarket).
			TimeInForce(futures.TimeInForceTypeGTC).
			//Quantity(qty).
			Quantity("0.002").
			TriggerPrice(marketSL).
			ReduceOnly(true).
			WorkingType(futures.WorkingTypeMarkPrice).
			Do(ctx)
		if IsImmediatelyTriggerError(err) {
			return emperror.Wrapf(entities.ErrImmediatelyTrigger, "transport.SetMarketSL")
		}
		if err != nil {
			return emperror.Wrapf(err, "transport.SetMarketSL")
		}
	}

	return nil
}
