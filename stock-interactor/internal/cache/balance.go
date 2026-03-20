package cache

func (b *CacheStruct) Balance() float64 {
	b.mu.Lock()
	defer b.mu.Unlock()

	return b.balance
}
