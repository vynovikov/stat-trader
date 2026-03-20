package streaminfo

type StreamInfo interface {
	ID() StreamID
	URL() string
	Name() string
	Method() string
}
