import grpc
import greet_pb2
import greet_pb2_grpc
from resnet50_split1 import front_model
from torchvision import transforms
from PIL import Image
import torch

def client():
    #------------------front passing-------------------
    model = front_model()
    model.eval()
    preprocess = transforms.Compose([
        transforms.Resize(256),           
        transforms.CenterCrop(224),       
        transforms.ToTensor(),            # Convert to tensor (HWC -> CHW)
        transforms.Normalize(             # Normalize with ImageNet mean and std
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
    img_path = 'car.jpg'
    img = Image.open(img_path).convert('RGB')
    img_tensor = preprocess(img)
    img_tensor = img_tensor.unsqueeze(0)

    with torch.no_grad():
        activations = model(img_tensor)

    activations_bytes = activations.cpu().numpy().tobytes()
    channels, height, width = activations.shape[1], activations.shape[2], activations.shape[3]

    img_request = greet_pb2.ImageRequest(
        activations = activations_bytes,
        height=height,
        width=width,
        channels=channels
    )
    with grpc.insecure_channel('127.0.0.1:50051') as channel:
        stub = greet_pb2_grpc.GreeterStub(channel)
        response = stub.SayHello(greet_pb2.HelloRequest(name='Chaitanya Sai', message='Hi server! nice to connect with you.'))
        print(f"Server replied: {response.message}")
        response = stub.SendImage(img_request)
        print(f"Server replied: {response.prediction}")

if __name__=="__main__":
    client()