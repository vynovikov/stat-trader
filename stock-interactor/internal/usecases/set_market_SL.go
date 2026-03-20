package usecases

import (
	"context"
	"sync"

	emperror "emperror.dev/errors"
	"github.com/vector-trader/stock-interactor/internal/entities"
)

func (d *domainStruct) setMarketSL(
	ctx context.Context,
	wg *sync.WaitGroup,
	symbol string,
	order entities.Order,
	marketSL string,

	chanErr chan error,
) {
	defer wg.Done()

	err := d.transport.SetMarketSL(
		ctx,
		symbol,
		order,
		marketSL,
	)

	if err != nil {
		chanErr <- emperror.Wrapf(err, "usecases.setLimitSL.transport.SetLimitSL")
	}
}
