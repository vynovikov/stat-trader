package transport

import (
	"context"

	"google.golang.org/grpc"
)

func shutdownRoutine(ctx context.Context, conn *grpc.ClientConn) {
	<-ctx.Done()
	conn.Close()

}
