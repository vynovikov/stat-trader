package candleworker

func (w *candleWorker) sendError(ch chan<- error, err error) {
	select {
	case ch <- err:
	default:
	}
}
