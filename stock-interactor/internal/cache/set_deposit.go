package cache

func (b *CacheStruct) SetBalance(Balance float64) {
	b.mu.Lock()
	defer b.mu.Unlock()

	b.balance = Balance
}
