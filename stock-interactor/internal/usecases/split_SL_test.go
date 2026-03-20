package usecases

import (
	"github.com/vector-trader/stock-interactor/internal/entities"
)

func (s *decideSuite) TestSplitSL() {
	tt := []struct {
		name               string
		domain             domainStruct
		order              entities.Order
		wantLimitSLTrigger string
		wantLimitSLPrice   string
		wantMarketSL       string
	}{
		{
			name: "0. CandleAction = BUY",
			domain: domainStruct{
				minPriceDelta: 1,
			},
			order: entities.Order{
				CandleAction: entities.CandleActionBuy,
				Entry:        1002,
				SL:           990.123456,
				TP:           1030,
				Volume:       500,
			},
			wantLimitSLTrigger: "1000",
			wantLimitSLPrice:   "990",
			wantMarketSL:       "980",
		},
		{
			name: "1. CandleAction = SELL",
			domain: domainStruct{
				minPriceDelta: 1,
			},
			order: entities.Order{
				CandleAction: entities.CandleActionSell,
				Entry:        1002,
				SL:           1020.123456,
				TP:           930,
				Volume:       500,
			},
			wantLimitSLTrigger: "1010",
			wantLimitSLPrice:   "1020",
			wantMarketSL:       "1030",
		},
	}

	for _, v := range tt {
		s.Run(v.name, func() {
			gotLimitSLTrigger, gotLimitSLPrice, gotMarketSL := v.domain.splitSL(v.order)

			s.Equal(v.wantLimitSLTrigger, gotLimitSLTrigger)
			s.Equal(v.wantLimitSLPrice, gotLimitSLPrice)
			s.Equal(v.wantMarketSL, gotMarketSL)

		})
	}
}
