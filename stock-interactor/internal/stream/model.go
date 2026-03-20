package stream

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

type WSConn struct {
	ID   streamInfo.StreamID
	Conn *websocket.Conn
}

type StreamID int

const (
	StreamRough StreamID = iota
	StreamFine
	StreamBook
)

const (
	emptyResultKey   = "result"
	emptyResultValue = "null"
)

var (
	errInitStreamResponse = fmt.Errorf("invalid initStream response")
)
