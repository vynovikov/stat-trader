package receiverworker

import (
	"context"
	"sync"

	"github.com/vector-trader/stock-interactor/internal/entities"
)

func (w *receiverWorker) Work(ctx context.Context, wg *sync.WaitGroup, symbol string, chanData <-chan entities.Candle, chanErr chan<- error) {
	defer wg.Done()

	for {
		select {
		case <-ctx.Done():
			return

		case data := <-chanData:
			spread := w.cache.Spread()
			balance := w.cache.Balance()

			w.domain.Decide(ctx, symbol, data, spread, balance)
		}
	}
}
