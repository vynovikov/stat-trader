package priceworker

import (
	"context"
	"strconv"
	"time"

	"github.com/vector-trader/stock-interactor/internal/entities"
)

func (w *priceWorker) handle(ctx context.Context) (float64, error) {
	var (
		data  aggTradeObj
		price float64
		err   error
	)

	backoff := time.Millisecond * 50

	select {
	case <-ctx.Done():
		return 0, ctx.Err()

	default:
		err = w.priceReader.Read(&data)
		if err != nil {
			for {
				w.logger.WarnContext(ctx, "[priceWorker] reconnecting ...")

				errReconnect := w.reconnect(ctx)
				if errReconnect != nil {

					select {
					case <-ctx.Done():
						return 0, ctx.Err()
					case <-time.After(backoff):
						backoff *= 2

						continue

					}
				}

				break
			}

			return 0, entities.ErrInvalidPrice
		}

		price, err = strconv.ParseFloat(data.Price, 64)
		if err != nil {

			return 0, err
		}
	}

	return price, nil
}
