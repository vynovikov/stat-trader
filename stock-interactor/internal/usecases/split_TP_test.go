package usecases

import (
	"github.com/vector-trader/stock-interactor/internal/entities"
)

func (s *decideSuite) TestSplitTP() {
	tt := []struct {
		name               string
		domain             domainStruct
		order              entities.Order
		wantLimitTPTrigger string
		wantLimitTPPrice   string
		wantMarketTP       string
	}{
		{
			name: "0. CandleAction = BUY",
			domain: domainStruct{
				minPriceDelta: 1,
			},
			order: entities.Order{
				CandleAction: entities.CandleActionBuy,
				Entry:        1002,
				SL:           990,
				TP:           1030.12345,
				Volume:       500,
			},
			wantLimitTPTrigger: "1020",
			wantLimitTPPrice:   "1030",
			wantMarketTP:       "1040",
		},
		{
			name: "1. CandleAction = SELL",
			domain: domainStruct{
				minPriceDelta: 1,
			},
			order: entities.Order{
				CandleAction: entities.CandleActionSell,
				Entry:        1002,
				SL:           1020,
				TP:           930.123456,
				Volume:       500,
			},
			wantLimitTPTrigger: "940",
			wantLimitTPPrice:   "930",
			wantMarketTP:       "920",
		},
	}

	for _, v := range tt {
		s.Run(v.name, func() {
			gotLimitTPTrigger, gotLimitTPPrice, gotMarketTP := v.domain.splitTP(v.order)

			s.Equal(v.wantLimitTPTrigger, gotLimitTPTrigger)
			s.Equal(v.wantLimitTPPrice, gotLimitTPPrice)
			s.Equal(v.wantMarketTP, gotMarketTP)

		})
	}
}
