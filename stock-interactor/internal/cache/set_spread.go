package cache

func (c *CacheStruct) SetSpread(spread float64) {
	c.mu.Lock()
	defer c.mu.Unlock()

	c.spread = spread
}
