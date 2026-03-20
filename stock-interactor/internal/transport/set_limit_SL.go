package transport

import (
	"context"
	"strconv"

	emperror "emperror.dev/errors"
	"github.com/adshao/go-binance/v2/futures"
	"github.com/vector-trader/stock-interactor/internal/entities"
)

func (t transportStruct) SetLimitSL(
	ctx context.Context,
	symbol string,
	order entities.Order,
	limitSLTrigger string,
	limitSLPrice string,
) error {
	side := oppositeSide(order.CandleAction)
	if side == "" {
		return emperror.New("transport.SetLimitSL: unknown candleAction")
	}

	if t.isTradingEnabled {
		_, err := t.stockClient.NewCreateAlgoOrderService().
			Symbol(symbol).
			Side(side).
			Type(futures.AlgoOrderTypeStop).
			TimeInForce(futures.TimeInForceTypeGTC).
			Price(limitSLPrice).
			TriggerPrice(limitSLTrigger).
			ReduceOnly(true).
			Quantity(strconv.FormatFloat(order.Volume, 'f', 3, 64)).
			Do(ctx)
		if IsImmediatelyTriggerError(err) {
			return emperror.Wrapf(entities.ErrImmediatelyTrigger, "transport.SetLimitSL")
		}
		if err != nil {
			return emperror.Wrapf(err, "transport.SetLimitSL")
		}
	}

	return nil
}
