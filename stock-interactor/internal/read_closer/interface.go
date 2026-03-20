package readcloser

import "time"

type Reader interface {
	Read(out any) error
	Close() error
	SetReadDeadline(t time.Time) error
}
