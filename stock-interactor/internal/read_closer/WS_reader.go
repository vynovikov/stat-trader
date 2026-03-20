package readcloser

import (
	"time"

	"github.com/gorilla/websocket"
)

type WSReader struct {
	conn        *websocket.Conn
	readTimeout time.Duration
}

func NewWSReader(conn *websocket.Conn, readTimeout time.Duration) *WSReader {
	return &WSReader{
		conn:        conn,
		readTimeout: readTimeout,
	}
}
