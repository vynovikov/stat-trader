package priceworker

import (
	"context"

	readCloser "github.com/vector-trader/stock-interactor/internal/read_closer"
	"github.com/vector-trader/stock-interactor/internal/stream"
)

func (w *priceWorker) reconnect(ctx context.Context) error {
	if w.priceReader != nil {
		_ = w.priceReader.Close()
	}

	conn, err := stream.InitStream(
		ctx,
		w.priceStreamInfo.URL(),
		w.priceStreamInfo.Name(),
		w.priceStreamInfo.Method(),
		w.priceStreamInfo.ID(),
		w.initTimeout,
		w.logger,
	)
	if err != nil {
		return err
	}

	w.priceReader = readCloser.NewWSReader(conn, w.readTimeout)

	return nil
}
