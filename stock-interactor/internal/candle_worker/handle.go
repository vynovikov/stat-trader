package candleworker

import (
	"context"
	"time"
)

func (w *candleWorker) handle(ctx context.Context) (klineObj, error) {
	var data klineData

	backoff := time.Millisecond * 100

	for {
		err := w.candleReader.Read(&data)
		if err == nil {
			//fmt.Printf("[%s] Open %s, High %s, Low %s, Close %s\n", time.Until(time.UnixMilli(data.Kline.CloseTime)).Round(time.Second), data.Kline.Open, data.Kline.High, data.Kline.Low, data.Kline.Close)

			return data.Kline, nil
		}

		select {
		case <-ctx.Done():
			return klineObj{}, ctx.Err()
		default:
			if err := w.reconnect(ctx); err == nil {
				backoff = time.Millisecond * 100

				continue
			}
		}

		select {
		case <-ctx.Done():
			return klineObj{}, ctx.Err()

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
