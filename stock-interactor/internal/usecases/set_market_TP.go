package usecases

import (
	"context"
	"sync"

	emperror "emperror.dev/errors"
	"github.com/vector-trader/stock-interactor/internal/entities"
)

func (d *domainStruct) setMarketTP(
	ctx context.Context,
	wg *sync.WaitGroup,
	symbol string,
	order entities.Order,
	marketTP string,
	chanErr chan error,
) {
	defer wg.Done()

	err := d.transport.SetMarketTP(
		ctx,
		symbol,
		order,
		marketTP,
	)
	if err != nil {
		chanErr <- emperror.Wrapf(err, "usecases.setLimitTP.transport.SetLimitTP")
	}
}
