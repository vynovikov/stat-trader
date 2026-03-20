package cache

import "github.com/vector-trader/stock-interactor/internal/entities"

// Candle retrieves cached candle
// Currently unused - see SetCandle for details
func (c *CacheStruct) Candle() entities.Candle {
	c.mu.Lock()
	defer c.mu.Unlock()

	return c.candle
}
