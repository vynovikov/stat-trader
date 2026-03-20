package api

import (
	"context"

	"github.com/vector-trader/stock-interactor/internal/pb"
)

func (a API) CloseOrder(ctx context.Context, req *pb.CloseOrderRequest) (*pb.CloseOrderResponse, error) {
	symbol := unmarshalCloseOrderRequest(req)

	profit, err := a.domain.CloseOrder(ctx, symbol)
	if err != nil {
		return nil, err
	}

	resp := marshalCloseOrderResponse(profit)

	return resp, nil
}
