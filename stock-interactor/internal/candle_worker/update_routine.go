package candleworker

import (
	"context"
	"errors"
	"time"

	emperror "emperror.dev/errors"
)

func (w *candleWorker) updateRoutine(ctx context.Context, chanError chan error) {
	ticker := time.NewTicker(time.Millisecond * 100)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return

		case <-ticker.C:
			data, err := w.handle(ctx)
			if errors.Is(err, errEmptyKline) {
				continue
			}
			if err != nil {
				w.sendError(chanError, emperror.Wrapf(err, "candleWorker.Work.handle"))
				continue
			}

			candle, err := toCandle(data)
			if err != nil {
				w.sendError(chanError, emperror.Wrapf(err, "candleWorker.Work.toCandle"))
				continue
			}

			//log.Printf("[candleWorker.Work] updateRoutine %v", time.Until(candle.CloseTime))

			w.cache.SetCandle(candle)

			w.metricsCollector.UpdateCandleMetrics(
				candle.Symbol,
				candle.Interval,
				candle.Open,
				candle.High,
				candle.Low,
				candle.Close,
				candle.Volume,
			)
		}
	}
}
