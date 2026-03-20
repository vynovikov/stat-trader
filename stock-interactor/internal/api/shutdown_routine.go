package api

import (
	"context"
	"net"

	"google.golang.org/grpc"
)

func shutdownRoutine(ctx context.Context, lis net.Listener, s *grpc.Server) {
	<-ctx.Done()
	s.GracefulStop()
	lis.Close()
}
