package candleworker

import "context"

func (w *candleWorker) shutdownRoutine(ctx context.Context) {
	<-ctx.Done()
	w.candleReader.Close()
}
