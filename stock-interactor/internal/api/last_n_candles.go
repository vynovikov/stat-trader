package api

import (
	"context"

	emperror "emperror.dev/errors"

	"github.com/vector-trader/stock-interactor/internal/pb"
)

func (a API) LastNCandles(ctx context.Context, req *pb.LastNRequest) (*pb.LastNResponse, error) {
	symbol, interval, limit := unmarshalLastNRequest(req)

	candles, err := a.domain.LastNCandles(ctx, symbol, interval, limit)
	if err != nil {
		return nil, emperror.Wrap(err, "api.LastNCandles")
	}

	resp := marshalLastNResponse(candles)

	return resp, nil
}
