import grpc
from concurrent import futures
import greet_pb2
import greet_pb2_grpc
from torchvision import models, transforms
from PIL import Image
import io
import torch
import numpy as np
from resnet50_split1 import back_model

model = back_model()
model.eval()

with open("imagenet_classes.txt", "r") as f:
    imagenet_labels = [line.strip() for line in f.readlines()]

class GreeterServicer(greet_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        print(f"message from client: {request.message}")
        return greet_pb2.HelloResponse(message=f"Hello! {request.name}, I am delighted to recieve message from you and I am happy too!")
    
    def SendImage(self, request, context):
        try:
            activations = request.activations # this is in bytes format
            height, width, channels = request.height, request.width, request.channels

            activation_array = np.frombuffer(activations, dtype=np.float32)
            activation_tensor = torch.from_numpy(activation_array).reshape(1, channels, height, width)

            with torch.no_grad():
                output = model(activation_tensor)
                _, pred_idx = torch.max(output, 1)
                pred = imagenet_labels[pred_idx]
            
            return greet_pb2.ImageResponse(prediction=f"The label of the image is {pred}")
        except Exception as e:
            context.set_details(f"Error processing image: {str(e)}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return greet_pb2.ImageResponse(label="Error")

def server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    greet_pb2_grpc.add_GreeterServicer_to_server(GreeterServicer(), server)
    server.add_insecure_port('[::]:50051')
    print('Server started and listening at port 50051!')
    server.start()
    server.wait_for_termination()

if __name__=="__main__":
    server()