package transport

import (
	"context"
	"log"

	emperror "emperror.dev/errors"
	"github.com/adshao/go-binance/v2/futures"
	"github.com/vector-trader/stock-interactor/internal/entities"
)

func (t transportStruct) SetMarketTP(
	ctx context.Context,
	symbol string,
	order entities.Order,
	marketTP string,
) error {
	side := oppositeSide(order.CandleAction)
	if side == "" {
		return emperror.New("transport.SetMarketTP: unknown candleAction")
	}

	log.Printf("[transport.SetMarketTP] side %v, marketTP %s", side, marketTP)

	if t.isTradingEnabled {
		_, err := t.stockClient.NewCreateAlgoOrderService().
			Symbol(symbol).
			Side(side).
			Type(futures.AlgoOrderTypeTakeProfitMarket).
			TriggerPrice(marketTP).
			ClosePosition(true).
			Do(ctx)
		if IsImmediatelyTriggerError(err) {
			return emperror.Wrapf(entities.ErrImmediatelyTrigger, "transport.SetMarketTP")
		}
		if err != nil {
			return emperror.Wrapf(err, "transport.SetMarketTP")
		}
	}

	return nil
}
