package usecases

import (
	"context"
	"errors"
	"sync"

	emperror "emperror.dev/errors"
	"github.com/vector-trader/stock-interactor/internal/entities"
)

func (d *domainStruct) setLimitSL(
	ctx context.Context,
	wg *sync.WaitGroup,
	symbol string,
	order entities.Order,
	limitSLTrigger string,
	limitSLPrice string,
	chanErr chan error,
) {
	defer wg.Done()

	err := d.transport.SetLimitSL(
		ctx,
		symbol,
		order,
		limitSLTrigger,
		limitSLPrice,
	)
	if errors.Is(err, entities.ErrImmediatelyTrigger) {
		errClose := d.transport.CloseOrder(ctx, symbol)
		if errClose != nil {

			chanErr <- emperror.Wrapf(errors.Join(err, errClose), "usecases.setLimitSL.transport.CloseOrder")
		}

		chanErr <- emperror.Wrapf(err, "usecases.setLimitSL.transport.SetLimitSL")
	}
}
