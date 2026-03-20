package cache

func (c *CacheStruct) Price() float64 {
	c.mu.Lock()
	defer c.mu.Unlock()

	return c.price
}
