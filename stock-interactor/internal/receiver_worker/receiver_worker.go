package receiverworker

import (
	"github.com/vector-trader/stock-interactor/internal/cache"
)

type receiverWorker struct {
	cache  cache.Cache
	domain domain
}

func NewReceiverWorker(cache cache.Cache, domain domain) *receiverWorker {
	return &receiverWorker{
		cache:  cache,
		domain: domain,
	}
}
