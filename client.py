import grpc
import greet_pb2
import greet_pb2_grpc

def client():
    
    img_path='santorini.jpeg'
    with open(img_path,'rb') as f:
        image_data = f.read()
    img_request = greet_pb2.ImageRequest(
        image = image_data,
        filename=img_path
    )
    with grpc.insecure_channel('127.0.0.1:50051') as channel:
        stub = greet_pb2_grpc.GreeterStub(channel)
        response = stub.SayHello(greet_pb2.HelloRequest(name='Chaitanya Sai', message='Hi server! nice to connect with you.'))
        print(f"Server replied: {response.message}")
        response = stub.SendImage(img_request)
        print(f"Server replied: {response.status}")

if __name__=="__main__":
    client()