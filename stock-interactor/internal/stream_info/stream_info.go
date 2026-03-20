package streaminfo

func NewStreamInfo(
	url, streamName, method string,
	id StreamID,
) streamInfo {
	return streamInfo{
		id:     id,
		url:    url,
		name:   streamName,
		method: method,
	}
}
