package cache

func (c *CacheStruct) Spread() float64 {
	c.mu.Lock()
	defer c.mu.Unlock()

	return c.spread
}
