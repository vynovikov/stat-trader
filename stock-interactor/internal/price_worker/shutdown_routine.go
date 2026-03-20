package priceworker

import "context"

func (w *priceWorker) shutdownRoutine(ctx context.Context) {
	<-ctx.Done()
	w.priceReader.Close()
}
