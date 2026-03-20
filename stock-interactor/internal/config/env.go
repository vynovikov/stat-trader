package config

import (
	emperror "emperror.dev/errors"
	envparse "github.com/caarlos0/env/v10"
)

type ENV struct {
	BinanceCandlesLimit    int    `env:"BINANCE_CANDLES_LIMIT" envDefault:"1000"`
	TransportSemaphoreSize int    `env:"TRANSPORT_SEMAPHORE_SIZE" envDefault:"4"`
	GRPCServerAddr         string `env:"GRPC_SERVER_ADDR" required:"true"`
	GRPCClientAddr         string `env:"GRPC_CLIENT_ADDR" required:"true"`
	MaxBackoff             string `env:"MAX_BACKOFF" envDefault:"8s"`
	ReadTimeout            string `env:"READ_TIMEOUT" envDefault:"5s"`
	RequestTimeout         string `env:"REQUEST_TIMEOUT" envDefault:"5s"`
	InitTimeout            string `env:"INIT_TIMEOUT" envDefault:"10s"`

	IsTradingEnabled bool   `env:"IS_TRADING_ENABLED" envDefault:"false"`
	Symbol           string `env:"SYMBOL" envDefault:"BTCUSDT"`
	MinPriceDelta    int    `env:"MIN_PRICE_DELTA" envDefault:"1"`

	WSURLCandle string `env:"WS_URL_CANDLE" envDefault:"wss://stream.binance.com:9443/ws"`
	WSURLPrice  string `env:"WS_URL_PRICE" envDefault:"wss://stream.binance.com:9443/ws"`
	WSURLBook   string `env:"WS_URL_BOOK" envDefault:"wss://stream.binance.com:9443/ws"`

	WSStreamNameCandle string `env:"WS_STREAM_NAME_CANDLE" envDefault:""`
	WSStreamNamePrice  string `env:"WS_STREAM_NAME_PRICE" envDefault:""`
	WSStreamNameBook   string `env:"WS_STREAM_NAME_BOOK" envDefault:""`

	WSMethodCandle string `env:"WS_METHOD_CANDLE" envDefault:""`
	WSMethodPrice  string `env:"WS_METHOD_PRICE" envDefault:""`

	BinanceAPIKey     string `env:"BINANCE_API_KEY" envDefault:""`
	BinanceSecretKey  string `env:"BINANCE_API_SECRET" envDefault:""`
	BinanceBaseURL    string `env:"BINANCE_BASE_URL" envDefault:""`
	BinanceHistoryURL string `env:"BINANCE_HISTORY_URL" envDefault:""`

	HistoryFilePath string `env:"HISTORY_FILE_PATH" envDefault:"./data/BTCUSDT_1m.csv"`
}

func Parse() (ENV, error) {
	var cfg ENV
	if err := envparse.Parse(&cfg); err != nil {
		return ENV{}, emperror.Wrapf(err, "failed to parse environment variables")
	}
	return cfg, nil
}
