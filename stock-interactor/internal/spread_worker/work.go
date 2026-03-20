package spreadworker

import (
	"context"
	"sync"
	"time"

	emperror "emperror.dev/errors"
)

func (w *spreadWorker) Work(ctx context.Context, wg *sync.WaitGroup, chanSpread chan float64, chanErr chan error) {
	defer wg.Done()

	go w.shutdownRoutine(ctx)

	ticker := time.NewTicker(100 * time.Millisecond)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			data, err := w.handle(ctx)
			if err != nil {
				w.sendError(chanErr, emperror.Wrapf(err, "spreadWorker.Work.handle"))
				continue
			}

			spread, err := calcSpread(data)
			if err != nil {
				if ctx.Err() != nil {
					return
				}

				w.sendError(chanErr, emperror.Wrapf(err, "spreadWorker.Work.calcSpread"))
				continue
			}

			w.cache.SetSpread(spread)

			select {
			case chanSpread <- spread:
			case <-ctx.Done():
				return
			default:
			}
		}
	}
}
