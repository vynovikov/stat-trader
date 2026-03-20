package usecases

import (
	"context"
	"sync"

	emperror "emperror.dev/errors"
	"github.com/vector-trader/stock-interactor/internal/entities"
)

func (d *domainStruct) setLimitTP(
	ctx context.Context,
	wg *sync.WaitGroup,
	symbol string,
	order entities.Order,
	limitTPTrigger string,
	limitTPPrice string,
	chanErr chan error,
) {
	defer wg.Done()

	err := d.transport.SetLimitTP(
		ctx,
		symbol,
		order,
		limitTPTrigger,
		limitTPPrice,
	)
	if err != nil {
		chanErr <- emperror.Wrapf(err, "usecases.setLimitTP.transport.SetLimitTP")
	}
}
