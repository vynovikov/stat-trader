package stream

import (
	"github.com/gorilla/websocket"
	streaminfo "github.com/vector-trader/stock-interactor/internal/stream_info"
)

type Stream interface {
	ID() streaminfo.StreamID
	Conn() *websocket.Conn
}
