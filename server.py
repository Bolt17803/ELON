import grpc
from concurrent import futures
import greet_pb2
import greet_pb2_grpc
from torchvision import models, transforms
from PIL import Image
import io
import torch

model = models.resnet50(pretrained=True)

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

with open("imagenet_classes.txt", "r") as f:
    imagenet_labels = [line.strip() for line in f.readlines()]

class GreeterServicer(greet_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        print(f"message from client: {request.message}")
        return greet_pb2.HelloResponse(message=f"Hello! {request.name}, I am delighted to recieve message from you and I am happy too!")
    
    def SendImage(self, request, context):
        try:
            img = request.image # this is in bytes format
            fname = request.filename
            print(f'file name: {fname}')
        
            filename = 'received.jpg'
            with open(filename, "wb") as f:
                f.write(img) # save the image in the server
            
            image = Image.open(io.BytesIO(img))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            image_tensor = preprocess(image)  # Apply transforms
            image_tensor = image_tensor.unsqueeze(0) # for adding batch dimension

            with torch.no_grad():
                output = model(image_tensor)
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