package usecases

import (
	"github.com/vector-trader/stock-interactor/internal/entities"
)

func (s *decideSuite) TestUpdateOrder() {
	tt := []struct {
		name      string
		domain    domainStruct
		order     entities.Order
		candle    entities.Candle
		lastPrice float64
		wantOrder entities.Order
	}{
		{
			name:   "0. BUY Price is not changed",
			domain: domainStruct{},
			candle: entities.Candle{
				Close: 1000,
			},
			order: entities.Order{
				CandleAction: entities.CandleActionBuy,
				Entry:        1002,
				SL:           990,
				TP:           1030,
				Volume:       500,
			},
			lastPrice: 1000,
			wantOrder: entities.Order{
				CandleAction: entities.CandleActionBuy,
				Entry:        1002,
				SL:           990,
				TP:           1030,
				Volume:       500,
			},
		},
		{
			name:   "1. BUY Price increased",
			domain: domainStruct{},
			candle: entities.Candle{
				Close: 1000,
			},
			order: entities.Order{
				CandleAction: entities.CandleActionBuy,
				Entry:        1002,
				SL:           990,
				TP:           1030,
				Volume:       500,
			},
			lastPrice: 1001,
			wantOrder: entities.Order{
				CandleAction: entities.CandleActionBuy,
				Entry:        1003,
				SL:           990,
				TP:           1030,
				Volume:       500,
			},
		},
		{
			name:   "2. BUY Price decreased",
			domain: domainStruct{},
			candle: entities.Candle{
				Close: 1000,
			},
			order: entities.Order{
				CandleAction: entities.CandleActionBuy,
				Entry:        1002,
				SL:           990,
				TP:           1030,
				Volume:       500,
			},
			lastPrice: 999,
			wantOrder: entities.Order{
				CandleAction: entities.CandleActionBuy,
				Entry:        1001,
				SL:           990,
				TP:           1030,
				Volume:       500,
			},
		},
		{
			name:   "3. SELL Price increased",
			domain: domainStruct{},
			candle: entities.Candle{
				Close: 1000,
			},
			order: entities.Order{
				CandleAction: entities.CandleActionSell,
				Entry:        1002,
				SL:           990,
				TP:           1030,
				Volume:       500,
			},
			lastPrice: 1001,
			wantOrder: entities.Order{
				CandleAction: entities.CandleActionSell,
				Entry:        1003,
				SL:           990,
				TP:           1030,
				Volume:       500,
			},
		},
		{
			name:   "4. SELL Price decreased",
			domain: domainStruct{},
			candle: entities.Candle{
				Close: 1000,
			},
			order: entities.Order{
				CandleAction: entities.CandleActionSell,
				Entry:        1002,
				SL:           990,
				TP:           1030,
				Volume:       500,
			},
			lastPrice: 999,
			wantOrder: entities.Order{
				CandleAction: entities.CandleActionSell,
				Entry:        1001,
				SL:           990,
				TP:           1030,
				Volume:       500,
			},
		},
	}

	for _, v := range tt {
		s.Run(v.name, func() {
			gotOrder := v.domain.updateOrder(v.order, v.candle, v.lastPrice)

			s.Equal(gotOrder, v.wantOrder)
		})
	}
}
