package candleworker

import (
	"fmt"
)

type klineData struct {
	EventType string   `json:"e"` // "kline"
	EventTime int64    `json:"E"` // event time (ms)
	Symbol    string   `json:"s"` // "BTCUSDT"
	Kline     klineObj `json:"k"` // сам объект свечи
}

type klineObj struct {
	OpenTime     int64  `json:"t"` // open time (ms)
	CloseTime    int64  `json:"T"` // close time (ms)
	Symbol       string `json:"s"`
	Interval     string `json:"i"` // "5m", "1m" и т.п.
	FirstTradeID int64  `json:"f"`
	LastTradeID  int64  `json:"L"`
	Open         string `json:"o"`
	Close        string `json:"c"`
	High         string `json:"h"`
	Low          string `json:"l"`
	Volume       string `json:"v"`
	Closed       bool   `json:"x"` // true — свеча закрыта
}

type aggTradeObj struct {
	EventType     string `json:"e"` // aggTrade
	EventTime     int64  `json:"E"`
	Symbol        string `json:"s"`
	TradeID       int64  `json:"a"`
	Price         string `json:"p"` // string!
	Quantity      string `json:"q"`
	FirstTradeID  int64  `json:"f"`
	LastTradeID   int64  `json:"l"`
	TradeTime     int64  `json:"T"`
	IsMarketMaker bool   `json:"m"`
}

type bookTickerObj struct {
	Symbol   string `json:"s"`
	BidPrice string `json:"b"`
	BidQty   string `json:"B"`
	AskPrice string `json:"a"`
	AskQty   string `json:"A"`
}

type subscription struct {
	Method string   `json:"method"`
	Params []string `json:"params"`
	ID     int      `json:"id"`
}

const (
	emptyResultKey   = "result"
	emptyResultValue = "null"
)

var (
	errEmptyKline         = fmt.Errorf("empty kline object")
	errEmptyAgg           = fmt.Errorf("empty aggTrade object")
	errInitStreamResponse = fmt.Errorf("invalid initStream response")
	errReadFailed         = fmt.Errorf("failed to read from stream")
)
