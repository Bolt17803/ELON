import grpc
import greet_pb2
import greet_pb2_grpc

def client():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = greet_pb2_grpc.GreeterStub(channel)
        response = stub.SayHello(greet_pb2.HelloRequest(name='Chaitanya Sai', message='I am happy to connect.'))
        print(f"Server replied: {response.message}")

if __name__=="__main__":
    client()