package entities

type Order struct {
	CandleAction CandleAction
	Entry        float64
	SL           float64
	TP           float64
	Volume       float64
}
