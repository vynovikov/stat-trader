package stream

import (
	"bytes"
	"context"
	"fmt"
	"log/slog"
	urlPkg "net/url"
	"sync"
	"time"

	"github.com/gorilla/websocket"
	streamInfo "github.com/vector-trader/stock-interactor/internal/stream_info"
)

func InitStreamConcurrent(
	ctx context.Context,
	wg *sync.WaitGroup,
	chanWSConn chan Stream,
	chanErr chan error,
	url, streamName, methodName string,
	id streamInfo.StreamID,
	timeout time.Duration,
	logger *slog.Logger,
) {
	defer wg.Done()

	for {

		select {
		case <-ctx.Done():
			return
		default:
			conn, err := InitStream(ctx, url, streamName, methodName, id, timeout, logger)

			if err != nil {
				select {
				case chanErr <- err:
					time.Sleep(100 * time.Millisecond)
					continue

				case <-ctx.Done():
					return
				}
			}

			select {
			case chanWSConn <- NewStream(id, conn):
				return

			case <-ctx.Done():
				return
			}
		}
	}
}

func InitStream(
	ctx context.Context,
	url, streamName, methodName string,
	id streamInfo.StreamID,
	timeout time.Duration,
	logger *slog.Logger,
) (*websocket.Conn, error) {
	var err error

	select {
	case <-ctx.Done():
		return nil, ctx.Err()

	default:
		if id == streamInfo.StreamBook || id == streamInfo.StreamPrice {
			url, err = urlPkg.JoinPath(url, streamName)
			if err != nil {
				return nil, err
			}
		}

		conn, _, err := websocket.DefaultDialer.DialContext(ctx, url, nil)
		if err != nil {
			if conn != nil {
				conn.Close()
			}
			return nil, err
		}

		initDeadline := time.Now().Add(timeout)
		conn.SetReadDeadline(initDeadline)
		conn.SetWriteDeadline(initDeadline)

		if len(streamName) > 0 && len(methodName) > 0 {

			sub := subscription{
				Method: methodName,
				Params: []string{streamName},
				ID:     int(id),
			}
			if err := conn.WriteJSON(sub); err != nil {
				conn.Close()
				return nil, err
			}

			_, msg, err := conn.ReadMessage()
			if err != nil {
				conn.Close()
				return nil, err
			}

			if !bytes.Contains(msg, []byte(emptyResultKey)) || !bytes.Contains(msg, []byte(emptyResultValue)) {
				conn.Close()
				return nil, errInitStreamResponse
			}
		}

		conn.SetReadDeadline(time.Time{})
		conn.SetWriteDeadline(time.Time{})

		switch id {
		case streamInfo.StreamBook, streamInfo.StreamPrice:
			logger.InfoContext(ctx, fmt.Sprintf("connected to %s", url))
		default:
			logger.InfoContext(ctx, fmt.Sprintf("connected to %s/%s", url, streamName))
		}

		return conn, nil
	}

}
