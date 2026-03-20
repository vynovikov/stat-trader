package entities

type MarketAction int
type CandleAction int

const (
	MarketActionHold MarketAction = iota
	MarketActionOpen
	MarketActionClose
	MarketActionCloseThenOpen
)

const (
	CandleActionNone CandleAction = iota
	CandleActionBuy
	CandleActionSell
)
