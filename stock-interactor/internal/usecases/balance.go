package usecases

import "context"

func (d domainStruct) Balance(ctx context.Context, symbol string) (float64, error) {

	return d.transport.Balance(ctx, symbol)
}
