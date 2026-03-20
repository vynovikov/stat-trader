package transport

import (
	"context"
	"strconv"
	"strings"

	emperror "emperror.dev/errors"
)

func (t transportStruct) Balance(ctx context.Context, symbol string) (float64, error) {
	balances, err := t.stockClient.NewGetBalanceService().Do(ctx)
	if err != nil {
		return 0, emperror.Wrap(err, "transport.Balance")
	}

	for _, b := range balances {
		if strings.HasSuffix(strings.ToTitle(symbol), strings.ToTitle(b.Asset)) {
			available, err := strconv.ParseFloat(b.AvailableBalance, 64)
			if err != nil {
				return 0, emperror.Wrap(err, "transport.Balance.ParseFloat")
			}

			return available, nil
		}
	}

	return 0, nil
}
