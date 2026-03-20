package priceworker

import (
	"context"
	"sync"
	"time"
)

func (w *priceWorker) Work(ctx context.Context, wg *sync.WaitGroup, chanTime chan time.Duration, chanErr chan error) {
	defer wg.Done()

	chanFreeze := make(chan struct{}, 1)

	go w.shutdownRoutine(ctx)

	for {
		select {
		case <-ctx.Done():
			return

		case <-w.stopTimer.C:
			select {
			case <-ctx.Done():
				return
			case untilCloseTime := <-chanTime:
				w.waitTimer = time.NewTimer(untilCloseTime - 500*time.Millisecond)
				w.stopTimer = time.NewTimer(untilCloseTime)

				chanFreeze <- struct{}{}
			}

		case <-chanFreeze:
			select {
			case <-ctx.Done():
				return
			case <-w.waitTimer.C:
				continue
			}

		default:
			price, err := w.handle(ctx)
			if err != nil {

				continue
			}

			w.cache.SetPrice(price)
		}
	}
}
