package entities

import "errors"

var (
	ErrInvalidPrice       = errors.New("invalid price")
	ErrInvalidLength      = errors.New("invalid length")
	ErrInvalidOpenTime    = errors.New("invalid open time")
	ErrInvalidCloseTime   = errors.New("invalid close time")
	ErrInvalidTradeCount  = errors.New("invalid trade count")
	ErrImmediatelyTrigger = errors.New("SL order would be triggered immediately")
)
