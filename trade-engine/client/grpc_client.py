import grpc

from client import interactor_pb2, interactor_pb2_grpc


class StockInteractorClient:
    def __init__(self, host="localhost", port=5000):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = interactor_pb2_grpc.HistoryServiceStub(self.channel)

    def get_history(self, symbol, interval, from_ts, to_ts):
        request = interactor_pb2.HistoryRequest(
            symbol=symbol,
            interval=interval,
            from_timestamp=from_ts,
            to_timestamp=to_ts,
        )
        for response in self.stub.GetHistory(request):
            yield response
