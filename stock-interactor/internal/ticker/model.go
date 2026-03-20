package ticker

import (
	"fmt"

	"github.com/gorilla/websocket"
	streamInfo "github.com/vector-trader/stock-interactor/internal/stream_info"
)

type subscription struct {
	Method string   `json:"method"`
	Params []string `json:"params"`
	ID     int      `json:"id"`
}

type wsConn struct {
	id   streamInfo.StreamID
	conn *websocket.Conn
}

const (
	emptyResultKey   = "result"
	emptyResultValue = "null"
)

var (
	errConnFailed         = fmt.Errorf("websocket connection failed")
	errInitStreamResponse = fmt.Errorf("invalid initStream response")
)
