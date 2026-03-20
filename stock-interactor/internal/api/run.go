package api

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"net"

	"github.com/vector-trader/stock-interactor/internal/config"
	"github.com/vector-trader/stock-interactor/internal/pb"
	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"
)

func Run(
	ctx context.Context,
	api API,
	cfg config.ENV,
	chanErr chan error,
) {
	lis, err := net.Listen("tcp", cfg.GRPCServerAddr)
	if err != nil {
		api.logger.ErrorContext(ctx, "api.Run", slog.String("apierror", err.Error()))

		return
	}

	s := grpc.NewServer()

	pb.RegisterStockServer(s, api)
	reflection.Register(s)

	go shutdownRoutine(ctx, lis, s)
	api.logger.InfoContext(ctx, fmt.Sprintf("gRPC server listening on %s", cfg.GRPCServerAddr))

	err = s.Serve(lis)
	if errors.Is(err, net.ErrClosed) {
		api.logger.InfoContext(ctx, "gRPC server closed gracefully")

		return
	}
	if err != nil {
		api.logger.ErrorContext(ctx, "failed to serve gRPC server", slog.String("error", fmt.Sprintf("%+v", err)))
	}
}
