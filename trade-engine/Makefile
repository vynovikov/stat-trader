.PHONY: proto clean pip

pip:
	pip install -r requirements.txt

test:
	@echo "🧪 Running tests..."
	pytest -v

proto_gen:
	@echo "🛠️  Generating protobuf code..."
	python3 -m grpc_tools.protoc \
		-I proto \
		--python_out=pb \
		--pyi_out=pb \
		--grpc_python_out=pb \
		proto/vector_trader.proto

	@echo "🔧 Fixing import in *_pb2_grpc.py..."
	sed -i 's/^import vector_trader_pb2/from . import vector_trader_pb2/' pb/vector_trader_pb2_grpc.py

clean:
	rm -f pb/vector_trader_pb2.py pb/vector_trader_pb2_grpc.py

image_push:
	docker buildx build \
		--platform linux/amd64,linux/arm64 \
		--push \
		-t ghcr.io/vynovikov/trade-engine:1.4 .