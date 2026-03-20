package transport

import (
	"context"
	"math"
	"strconv"

	emperror "emperror.dev/errors"
	"github.com/adshao/go-binance/v2/futures"
)

func (t transportStruct) CloseOrder(ctx context.Context, symbol string) error {
	positions, err := t.stockClient.NewGetPositionRiskService().
		Symbol(symbol).
		Do(ctx)
	if err != nil {
		return emperror.Wrapf(err, "transport.CloseOrder.NewGetPositionRiskService")
	}
	if len(positions) == 0 {
		t.logger.WarnContext(ctx, "transport.CloseOrder no positions found")
		return nil
	}

	position := positions[0]

	if t.isTradingEnabled {
		var amt float64
		err = t.stockClient.NewCancelAllAlgoOpenOrdersService().
			Symbol(symbol).
			Do(ctx)
		if err != nil {
			t.logger.WarnContext(ctx, "transport.CloseOrder failed to cancel algo orders", "err", err)
		}

		amt, err = strconv.ParseFloat(position.PositionAmt, 64)
		if err != nil {
			return emperror.Wrapf(err, "transport.CloseOrder.ParseFloat")
		}

		if amt == 0 {
			t.logger.WarnContext(ctx, "transport.CloseOrder position amount is zero")
			return nil
		}

		var side futures.SideType
		if amt != 0 {

			if amt > 0 {
				side = futures.SideTypeSell
			} else {
				side = futures.SideTypeBuy
			}
		}

		qty := math.Abs(amt)
		qStr := strconv.FormatFloat(qty, 'f', -1, 64)

		_, err = t.stockClient.NewCreateOrderService().
			Symbol(symbol).
			Side(side).
			Type(futures.OrderTypeMarket).
			Quantity(qStr).
			ReduceOnly(true).
			Do(ctx)
		if err != nil {
			return emperror.Wrapf(err, "transport.CloseOrder.NewCreateOrderService")
		}
	}

	return nil
}
