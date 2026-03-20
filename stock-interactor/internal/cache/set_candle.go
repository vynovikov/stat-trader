package cache

import (
	entities "github.com/vector-trader/stock-interactor/internal/entities"
)

func (c *CacheStruct) SetCandle(candle entities.Candle) {
	c.mu.Lock()
	defer c.mu.Unlock()

	//log.Printf("[%v] Open %.0f, Close %0.0f, High %.0f, Low %.0f", time.Until(candle.CloseTime), candle.Open, candle.Close, candle.High, candle.Low)

	c.candle = candle
}
