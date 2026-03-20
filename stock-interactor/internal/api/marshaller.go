package api

import (
	"github.com/vector-trader/stock-interactor/internal/entities"
	"github.com/vector-trader/stock-interactor/internal/pb"
	"google.golang.org/protobuf/types/known/timestamppb"
)

func marshalCandle(candle entities.Candle) *pb.Candle {
	return &pb.Candle{
		Open:      candle.Open,
		Close:     candle.Close,
		High:      candle.High,
		Low:       candle.Low,
		Volume:    candle.Volume,
		OpenTime:  timestamppb.New(candle.OpenTime),
		CloseTime: timestamppb.New(candle.CloseTime),
	}
}

func unmarshalLastNRequest(req *pb.LastNRequest) (string, string, int) {
	if req == nil {
		return "", "", 0
	}
	return req.GetSymbol(), req.GetInterval(), int(req.GetLimit())
}

func marshalLastNResponse(candles []entities.Candle) *pb.LastNResponse {
	if len(candles) == 0 {
		return &pb.LastNResponse{}
	}

	marshalledCandles := make([]*pb.Candle, len(candles))
	for i, candle := range candles {
		marshalledCandles[i] = marshalCandle(candle)
	}

	return &pb.LastNResponse{
		Candles: marshalledCandles,
	}
}

func unmarshalIntervalCandlesRequest(req *pb.IntervalCandlesRequest) (string, string, int64, int64) {
	if req == nil {
		return "", "", 0, 0
	}
	return req.GetSymbol(), req.GetInterval(), req.GetFromTimestamp(), req.GetToTimestamp()
}

func marshalIntervalCandlesResponse(candles []entities.Candle) (*pb.IntervalCandlesResponse, error) {
	if len(candles) == 0 {
		return &pb.IntervalCandlesResponse{}, nil
	}

	marshalledCandles := make([]*pb.Candle, len(candles))

	for i, candle := range candles {
		marshalledCandles[i] = marshalCandle(candle)
	}

	return &pb.IntervalCandlesResponse{
		Candles: marshalledCandles,
	}, nil
}

func unmarshalOpenOrderRequest(req *pb.OpenOrderRequest) (string, entities.Order) {
	if req == nil {
		return "", entities.Order{}
	}

	order := entities.Order{
		CandleAction: entities.CandleAction(req.GetOrder().GetCandleAction()),
		Entry:        req.GetOrder().GetEntry(),
		SL:           req.GetOrder().GetSl(),
		TP:           req.GetOrder().GetTp(),
		Volume:       req.GetOrder().GetVolume(),
	}

	return req.GetSymbol(), order
}

func marshalOpenOrderResponse(orderID string) *pb.OpenOrderResponse {
	return &pb.OpenOrderResponse{
		OrderId: orderID,
	}
}

func unmarshalCloseOrderRequest(req *pb.CloseOrderRequest) string {
	if req == nil {
		return ""
	}
	return req.GetSymbol()
}

func marshalCloseOrderResponse(profit float64) *pb.CloseOrderResponse {
	return &pb.CloseOrderResponse{
		Profit: profit,
	}
}
