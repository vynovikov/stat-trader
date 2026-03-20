package readcloser

import "time"

func (r *WSReader) Read(out any) error {
	if r.readTimeout > 0 {
		r.conn.SetReadDeadline(time.Now().Add(r.readTimeout))
	}

	return r.conn.ReadJSON(out)
}
