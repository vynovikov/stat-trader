package api

import (
	"context"

	"github.com/vector-trader/stock-interactor/internal/pb"
)

func (a API) OpenOrder(ctx context.Context, req *pb.OpenOrderRequest) (*pb.OpenOrderResponse, error) {
	symbol, order := unmarshalOpenOrderRequest(req)

	err := a.domain.OpenOrder(ctx, symbol, order)
	if err != nil {
		return nil, err
	}

	resp := marshalOpenOrderResponse("")

	return resp, nil
}
