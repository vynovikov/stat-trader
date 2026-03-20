package transport

import (
	"context"
	"log"

	emperror "emperror.dev/errors"
	"github.com/adshao/go-binance/v2/futures"
	"github.com/vector-trader/stock-interactor/internal/entities"
)

func (t transportStruct) SetLimitTP(
	ctx context.Context,
	symbol string,
	order entities.Order,
	limitTPTrigger string,
	limitTPPrice string,
) error {
	side := oppositeSide(order.CandleAction)
	if side == "" {
		return emperror.New("transport.SetLimitTP: unknown candleAction")
	}

	//qty := strings.TrimRight(strings.TrimRight(strconv.FormatFloat(order.Volume, 'f', 3, 64), "0"), ".")

	log.Printf("[transport.SetLimitTP] side %v, limitTPTrigger %s, limitTPPrice %s", side, limitTPTrigger, limitTPPrice)

	if t.isTradingEnabled {
		_, err := t.stockClient.NewCreateAlgoOrderService().
			Symbol(symbol).
			Side(side).
			Type(futures.AlgoOrderTypeTakeProfit).
			TimeInForce(futures.TimeInForceTypeGTC).
			//Quantity(qty).
			Quantity("0.002").
			TriggerPrice(limitTPTrigger).
			Price(limitTPPrice).
			ReduceOnly(true).
			WorkingType(futures.WorkingTypeMarkPrice).
			Do(ctx)
		if IsImmediatelyTriggerError(err) {
			return emperror.Wrapf(entities.ErrImmediatelyTrigger, "transport.SetLimitTP")
		}
		if err != nil {
			return emperror.Wrapf(err, "transport.SetLimitTP")
		}
	}

	return nil
}
