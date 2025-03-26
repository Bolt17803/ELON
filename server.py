import grpc
from concurrent import futures
import greet_pb2
import greet_pb2_grpc

class GreeterServicer(greet_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        print(f"message from client: {request.message}")
        return greet_pb2.HelloResponse(message=f"Hello! {request.name}, I am delighted to recieve message from you and I am happy too!")
    
    def SendImage(self, request, context):
        print("Image received from the client")
        img = request.image
        fname = request.filename
        filename = 'received.jpg'
        with open(filename, "wb") as f:
            f.write(img)
        return greet_pb2.ImageResponse(status=f"Successful !!! the image {fname} is received by the server")

def server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    greet_pb2_grpc.add_GreeterServicer_to_server(GreeterServicer(), server)
    server.add_insecure_port('[::]:50051')
    print('Server started and listening at port 50051!')
    server.start()
    server.wait_for_termination()

if __name__=="__main__":
    server()