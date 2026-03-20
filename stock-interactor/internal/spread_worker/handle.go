package spreadworker

import (
	"context"
	"log"
	"time"
)

func (w *spreadWorker) handle(ctx context.Context) (bookTickerObj, error) {
	var data bookTickerObj

	backoff := time.Millisecond * 400

	for {
		err := w.bookReader.Read(&data)
		if err == nil {
			return data, nil
		}
		log.Println("[spreadWorker.handle] error", err)

		select {
		case <-ctx.Done():
			return bookTickerObj{}, ctx.Err()
		default:
			if err := w.reconnect(ctx); err == nil {
				backoff = time.Millisecond * 100

				continue
			}
		}

		select {
		case <-ctx.Done():
			return bookTickerObj{}, ctx.Err()

		case <-time.After(backoff):
		}

		if backoff < w.maxBackoff {
			backoff *= 2

			if backoff > w.maxBackoff {
				backoff = w.maxBackoff
			}
		}
	}
}
