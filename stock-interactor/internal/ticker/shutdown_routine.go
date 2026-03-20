package ticker

import (
	"context"

	readcloser "github.com/vector-trader/stock-interactor/internal/read_closer"
)

func shutdownRoutine(
	ctx context.Context,
	readers ...readcloser.Reader,
) {
	<-ctx.Done()

	for _, reader := range readers {
		if reader == nil {
			continue
		}

		_ = reader.Close()
	}
}
