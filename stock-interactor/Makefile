proto_gen:
	protoc \
		--proto_path=internal/proto \
		--go_out=internal/pb --go_opt=paths=source_relative \
		--go-grpc_out=internal/pb --go-grpc_opt=paths=source_relative \
		internal/proto/vector_trader.proto

image_push:
	docker buildx build \
		--platform linux/amd64,linux/arm64 \
		--push \
		-t ghcr.io/vynovikov/stock-interactor:1.4 .