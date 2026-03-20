package usecases

import (
	"context"
)

func (d *domainStruct) CloseOrder(ctx context.Context, symbol string) (float64, error) {
	return 0, d.transport.CloseOrder(ctx, symbol)
}
