package streaminfo

type StreamID int

const (
	StreamCandle StreamID = iota
	StreamPrice
	StreamBook
)

type streamInfo struct {
	id     StreamID
	url    string
	name   string
	method string
}

type StreamsInfo struct {
	Candle StreamInfo
	Price  StreamInfo
	Book   StreamInfo
}
