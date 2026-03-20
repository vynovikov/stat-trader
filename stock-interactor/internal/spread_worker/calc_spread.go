package spreadworker

import (
	"strconv"
)

func calcSpread(book bookTickerObj) (float64, error) {
	bid, err := strconv.ParseFloat(book.BidPrice, 64)
	if err != nil {
		return 0, err
	}

	ask, err := strconv.ParseFloat(book.AskPrice, 64)
	if err != nil {
		return 0, err
	}

	spread := ask - bid

	return spread, nil
}
