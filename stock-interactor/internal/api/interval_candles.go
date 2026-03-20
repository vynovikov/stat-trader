package api

import (
	"context"

	emperror "emperror.dev/errors"
	"github.com/vector-trader/stock-interactor/internal/pb"
)

func (a API) IntervalCandles(
	ctx context.Context,
	req *pb.IntervalCandlesRequest,
) (*pb.IntervalCandlesResponse, error) {
	symbol, interval, fromTS, toTs := unmarshalIntervalCandlesRequest(req)

	candles, err := a.domain.IntervalCandles(ctx, symbol, interval, fromTS, toTs)
	if err != nil {
		return nil, emperror.Wrap(err, "api.IntervalCandles")
	}

	if len(candles) == 0 {
		return &pb.IntervalCandlesResponse{}, nil
	}

	result, err := marshalIntervalCandlesResponse(candles)
	if err != nil {
		return nil, emperror.Wrap(err, "api.IntervalCandles")
	}

	return result, nil
}
