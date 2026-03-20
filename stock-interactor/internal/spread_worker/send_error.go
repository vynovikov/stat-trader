package spreadworker

func (w *spreadWorker) sendError(ch chan<- error, err error) {
	select {
	case ch <- err:
	default:
	}
}
