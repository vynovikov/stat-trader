package readcloser

func (r *WSReader) Close() error {
	return r.conn.Close()
}
