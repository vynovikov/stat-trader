package spreadworker

import (
	"context"

	readCloser "github.com/vector-trader/stock-interactor/internal/read_closer"
	"github.com/vector-trader/stock-interactor/internal/stream"
)

func (w *spreadWorker) reconnect(ctx context.Context) error {
	if w.bookReader != nil {
		_ = w.bookReader.Close()
	}

	conn, err := stream.InitStream(
		ctx,
		w.bookStreamInfo.URL(),
		w.bookStreamInfo.Name(),
		w.bookStreamInfo.Method(),
		w.bookStreamInfo.ID(),
		w.initTimeout,
		w.logger,
	)
	if err != nil {
		return err
	}

	w.bookReader = readCloser.NewWSReader(conn, w.readTimeout)

	return nil
}
