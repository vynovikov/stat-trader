package metrics

type MetricsCollector interface {
	UpdateCandleMetrics(
		symbol, interval string,
		open, high, low, close, volume float64,
	)
}
