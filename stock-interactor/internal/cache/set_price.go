package cache

func (c *CacheStruct) SetPrice(price float64) {
	c.mu.Lock()
	defer c.mu.Unlock()

	c.price = price

}
