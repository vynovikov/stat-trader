package metrics

import (
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

type MetricsCollectorStruct struct {
	candleOpen   *prometheus.GaugeVec
	candleHigh   *prometheus.GaugeVec
	candleLow    *prometheus.GaugeVec
	candleClose  *prometheus.GaugeVec
	candleVolume *prometheus.GaugeVec
}

func NewMetricsCollector() *MetricsCollectorStruct {
	candleOpen := promauto.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "candle_open",
			Help: "Current candle open price",
		},
		[]string{"symbol", "interval"},
	)

	candleHigh := promauto.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "candle_high",
			Help: "Current candle high price",
		},
		[]string{"symbol", "interval"},
	)

	candleLow := promauto.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "candle_low",
			Help: "Current candle low price",
		},
		[]string{"symbol", "interval"},
	)

	candleClose := promauto.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "candle_close",
			Help: "Current candle close price",
		},
		[]string{"symbol", "interval"},
	)

	candleVolume := promauto.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "candle_volume",
			Help: "Current candle volume",
		},
		[]string{"symbol", "interval"},
	)

	return &MetricsCollectorStruct{
		candleOpen:   candleOpen,
		candleHigh:   candleHigh,
		candleLow:    candleLow,
		candleClose:  candleClose,
		candleVolume: candleVolume,
	}
}
