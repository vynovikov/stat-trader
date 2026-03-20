package candleworker

import "strconv"

func unmarshallKline(data klineObj) (string, string, float64, float64, float64, float64, float64) {
	symbol := data.Symbol
	interval := data.Interval

	open, _ := strconv.ParseFloat(data.Open, 64)
	high, _ := strconv.ParseFloat(data.High, 64)
	low, _ := strconv.ParseFloat(data.Low, 64)
	close, _ := strconv.ParseFloat(data.Close, 64)
	volume, _ := strconv.ParseFloat(data.Volume, 64)

	return symbol, interval, open, high, low, close, volume
}
