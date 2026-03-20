package priceworker

type aggTradeObj struct {
	EventType     string `json:"e"`
	EventTime     int64  `json:"E"`
	Symbol        string `json:"s"`
	TradeID       int64  `json:"a"`
	Price         string `json:"p"`
	Quantity      string `json:"q"`
	FirstTradeID  int64  `json:"f"`
	LastTradeID   int64  `json:"l"`
	TradeTime     int64  `json:"T"`
	IsMarketMaker bool   `json:"m"`
}
