package transport

import (
	"context"
	"log/slog"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"

	"github.com/vector-trader/stock-interactor/internal/config"

	emperror "emperror.dev/errors"
	"github.com/adshao/go-binance/v2/futures"
	"github.com/vector-trader/stock-interactor/internal/pb"
)

type transportStruct struct {
	limit            int
	stockClient      *futures.Client
	engineClient     pb.EngineClient
	engineConn       *grpc.ClientConn
	isTradingEnabled bool
	requestTimeout   time.Duration
	logger           *slog.Logger
}

func New(ctx context.Context, cfg config.ENV, logger *slog.Logger) (transportStruct, error) {
	stockClient := futures.NewClient(cfg.BinanceAPIKey, cfg.BinanceSecretKey)

	requestTimeout, err := time.ParseDuration(cfg.RequestTimeout)
	if err != nil {
		return transportStruct{}, emperror.Wrap(err, "transport.New")
	}

	engineConn, err := grpc.NewClient(
		cfg.GRPCClientAddr,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
	)
	if err != nil {
		return transportStruct{}, emperror.Wrap(err, "transport.New")
	}

	go shutdownRoutine(ctx, engineConn)

	engineClient := pb.NewEngineClient(engineConn)

	return transportStruct{
		limit:            cfg.BinanceCandlesLimit,
		stockClient:      stockClient,
		engineClient:     engineClient,
		engineConn:       engineConn,
		isTradingEnabled: cfg.IsTradingEnabled,
		requestTimeout:   requestTimeout,
		logger:           logger,
	}, nil
}
