package stream

import "github.com/gorilla/websocket"

func (s streamStruct) Conn() *websocket.Conn {
	return s.conn
}
