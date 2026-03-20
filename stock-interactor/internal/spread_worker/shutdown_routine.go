package spreadworker

import (
	"context"
)

func (w *spreadWorker) shutdownRoutine(ctx context.Context) {
	<-ctx.Done()
	w.bookReader.Close()
}
