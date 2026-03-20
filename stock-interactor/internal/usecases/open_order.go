package usecases

import (
	"context"
	"log"

	"github.com/vector-trader/stock-interactor/internal/entities"
)

func (d *domainStruct) OpenOrder(ctx context.Context, symbol string, order entities.Order) error {
	err := d.transport.OpenOrder(ctx, symbol, order)
	if err != nil {
		log.Println("[domain.OpenOrder] error", err)
		return err
	}

	return nil
}
