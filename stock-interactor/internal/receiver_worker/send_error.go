package receiverworker

func (w *receiverWorker) sendError(ch chan<- error, err error) {
	select {
	case ch <- err:
	default:
	}
}
