package candleworker

import (
	"context"

	readCloser "github.com/vector-trader/stock-interactor/internal/read_closer"
	"github.com/vector-trader/stock-interactor/internal/stream"
)

func (w *candleWorker) reconnect(ctx context.Context) error {
	if w.candleReader != nil {
		_ = w.candleReader.Close()
	}

	conn, err := stream.InitStream(
		ctx,
		w.candleStreamInfo.URL(),
		w.candleStreamInfo.Name(),
		w.candleStreamInfo.Method(),
		w.candleStreamInfo.ID(),
		w.initTimeout,
		w.logger,
	)
	if err != nil {
		return err
	}

	w.candleReader = readCloser.NewWSReader(conn, w.readTimeout)

	return nil
}
