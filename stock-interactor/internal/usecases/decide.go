package usecases

import (
	"context"
	"fmt"
	"log"
	"sync"
	"time"

	emperror "emperror.dev/errors"

	"github.com/vector-trader/stock-interactor/internal/entities"
)

func (d *domainStruct) Decide(
	ctx context.Context,
	symbol string,
	candle entities.Candle,
	spread float64,
	balance float64,
) {
	d.logger.InfoContext(ctx, "--------------------------------------------------------------------------------------------------------------")

	switch {
	case candle.Close > candle.Open:
		d.logger.InfoContext(ctx,
			fmt.Sprintf("usecases.Decide candle [UP]: High %.0f, Low: %.0f, Open %.0f, Close %.0f, OpenTime %s, CloseTime %s",
				candle.High,
				candle.Low,
				candle.Open,
				candle.Close,
				candle.OpenTime.Round(time.Second).Add(3*time.Hour).Format("2006-01-02 15:04:05"),
				candle.CloseTime.Round(time.Second).Add(3*time.Hour).Format("2006-01-02 15:04:05"),
			),
		)
	case candle.Close < candle.Open:
		d.logger.InfoContext(ctx,
			fmt.Sprintf("usecases.Decide candle [DOWN]: High %.0f, Low: %.0f, Open %.0f, Close %.0f, OpenTime %s, CloseTime %s",
				candle.High,
				candle.Low,
				candle.Open,
				candle.Close,
				candle.OpenTime.Round(time.Second).Add(3*time.Hour).Format("2006-01-02 15:04:05"),
				candle.CloseTime.Round(time.Second).Add(3*time.Hour).Format("2006-01-02 15:04:05"),
			),
		)
	}

	decision, err := d.transport.Decide(ctx, candle, spread, balance)
	if err != nil {
		d.chanErr <- emperror.Wrapf(err, "usecases.Decide")
	}

	order := d.getOrder(decision)

	d.logger.InfoContext(ctx, fmt.Sprintf("[domain.Decide] action %v, order %#v", decision.MarketAction, order))

	switch decision.MarketAction {
	case entities.MarketActionOpen:
		var updatedOrder entities.Order

		lastPrice := d.cache.Price()
		updatedOrder = d.updateOrder(decision.Order, candle, lastPrice)

		if err := d.OpenOrder(ctx, symbol, updatedOrder); err != nil {
			d.chanErr <- emperror.Wrapf(err, "usecases.Decide.OpenOrder")

			return
		}

		log.Println("[usecases.Decide] order opened")

		_, _, marketSL := d.splitSL(updatedOrder)
		limitTPTrigger, limitTPPrice, _ := d.splitTP(updatedOrder)

		var wg sync.WaitGroup

		wg.Add(2)
		go d.setMarketSL(ctx, &wg, symbol, updatedOrder, marketSL, d.chanErr)
		go d.setLimitTP(ctx, &wg, symbol, updatedOrder, limitTPTrigger, limitTPPrice, d.chanErr)
		wg.Wait()
	}
}
