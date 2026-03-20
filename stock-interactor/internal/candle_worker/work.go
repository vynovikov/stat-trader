package candleworker

import (
	"context"
	"sync"
	"time"

	emperror "emperror.dev/errors"
	"github.com/vector-trader/stock-interactor/internal/entities"
)

func (w *candleWorker) Work(
	ctx context.Context,
	wg *sync.WaitGroup,
	symbol string,
	chanCandle chan entities.Candle,
	chanTime chan time.Duration,
	chanError chan error,
) {
	defer wg.Done()

	go w.shutdownRoutine(ctx)
	go w.updateRoutine(ctx, chanError)

	for {
		select {
		case <-ctx.Done():
			return
		case <-w.startIn.C:

			var (
				tryCount       int
				untilCloseTime time.Duration
			)

			for { // Wait for new candle
				cachedCandle := w.cache.Candle()
				candleMaxDuration := cachedCandle.CloseTime.Sub(cachedCandle.OpenTime)

				untilCloseTime = time.Until(cachedCandle.CloseTime)

				if untilCloseTime < 0 || untilCloseTime > candleMaxDuration {

					tryCount++

					if tryCount >= 10 {
						w.sendError(chanError, emperror.Wrap(errReadFailed, "candleWorker.Work"))
						return
					}
					time.Sleep(250 * time.Millisecond)
					continue
				}

				break
			}
			chanTime <- untilCloseTime

			w.stopIn = time.NewTimer(untilCloseTime - 500*time.Millisecond)
			w.startIn = time.NewTimer(untilCloseTime + 5*time.Second)

			balance, _ := w.domain.Balance(ctx, symbol)

			w.cache.SetBalance(balance)

		case <-w.stopIn.C:
			cacheCandle := w.cache.Candle()

			chanCandle <- cacheCandle
		}
	}
}
