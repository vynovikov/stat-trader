package readcloser

import "time"

func (r *WSReader) SetReadDeadline(t time.Time) error {
	return r.conn.SetReadDeadline(t)
}
