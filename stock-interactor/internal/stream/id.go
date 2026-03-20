package stream

import streaminfo "github.com/vector-trader/stock-interactor/internal/stream_info"

func (s streamStruct) ID() streaminfo.StreamID {
	return s.id
}
