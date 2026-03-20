package transport

import (
	"errors"

	"github.com/adshao/go-binance/v2/common"
)

func IsImmediatelyTriggerError(err error) bool {
	var apiErr *common.APIError
	if errors.As(err, &apiErr) {
		return apiErr.Code == IMMEDIATELY_TRIGGER_CODE
	}
	return false
}
