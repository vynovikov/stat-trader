package transport

import (
	"context"

	emperror "emperror.dev/errors"
	"github.com/vector-trader/stock-interactor/internal/entities"
	"github.com/vector-trader/stock-interactor/internal/pb"
	"google.golang.org/protobuf/types/known/timestamppb"
)

func (t transportStruct) Decide(ctx context.Context, candle entities.Candle, spread float64, balance float64) (entities.Decision, error) {

	resp, err := t.engineClient.Decide(ctx, &pb.DecideRequest{
		Candle: &pb.Candle{
			Open:      candle.Open,
			High:      candle.High,
			Low:       candle.Low,
			Close:     candle.Close,
			Volume:    candle.Volume,
			OpenTime:  timestamppb.New(candle.OpenTime),
			CloseTime: timestamppb.New(candle.CloseTime),
		},
		Spread:  0.01,
		Balance: balance,
	})
	if err != nil {
		return entities.Decision{}, emperror.Wrapf(err, "transport.Decide")
	}

	decision := unmarshalDecision(resp)

	return decision, nil
}
