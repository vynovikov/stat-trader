package stream

import (
	"github.com/gorilla/websocket"
	streaminfo "github.com/vector-trader/stock-interactor/internal/stream_info"
)

type streamStruct struct {
	id   streaminfo.StreamID
	conn *websocket.Conn
}

func NewStream(id streaminfo.StreamID, conn *websocket.Conn) streamStruct {
	return streamStruct{
		id:   id,
		conn: conn,
	}
}
