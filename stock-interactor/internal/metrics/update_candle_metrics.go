package metrics

import "github.com/prometheus/client_golang/prometheus"

func (m *MetricsCollectorStruct) UpdateCandleMetrics(
	symbol, interval string,
	open, high, low, close, volume float64,
) {
	labels := prometheus.Labels{
		"symbol":   symbol,
		"interval": interval,
	}

	m.candleOpen.With(labels).Set(open)
	m.candleHigh.With(labels).Set(high)
	m.candleLow.With(labels).Set(low)
	m.candleClose.With(labels).Set(close)
	m.candleVolume.With(labels).Set(volume)
}
