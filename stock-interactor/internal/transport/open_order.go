package transport

import (
	"context"
	"fmt"
	"log"
	"strconv"

	emperror "emperror.dev/errors"
	"github.com/adshao/go-binance/v2/futures"

	"github.com/vector-trader/stock-interactor/internal/entities"
)

func (t transportStruct) OpenOrder(
	ctx context.Context,
	symbol string,
	order entities.Order,
) error {
	side := side(order.CandleAction)

	if t.isTradingEnabled {
		t.logger.InfoContext(ctx,
			fmt.Sprintf("[Transport.OpenOrder] order: %+v, qty %s", order, fmt.Sprintf("%.3f", order.Volume)),
		)

		//qty := strings.TrimRight(strings.TrimRight(strconv.FormatFloat(order.Volume, 'f', 3, 64), "0"), ".")

		_, err := t.stockClient.NewCreateOrderService().
			Symbol(symbol).
			Side(side).
			Type(futures.OrderTypeLimit).
			TimeInForce(futures.TimeInForceTypeGTC).
			//Quantity(qty).
			Quantity("0.002").
			Price(strconv.FormatFloat(order.Entry, 'f', 1, 64)).
			Do(ctx)
		if err != nil {
			log.Println("[Transport.OpenOrder] error", err)
			return emperror.Wrapf(err, "transport.OpenOrder")
		}
	}

	return nil
}
