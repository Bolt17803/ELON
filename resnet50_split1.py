from torchvision import models
import torch

def resnet50():
    return models.resnet50(weights=models.ResNet50_Weights)

class front_model(torch.nn.Module):
    def __init__(self):
        super().__init__()

        model=resnet50()

        self.conv1 = model.conv1
        self.bn1 = model.bn1
        self.act1 = model.relu
        self.pool = model.maxpool

        for p in self.parameters():
            p.requires_grad = False

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.act1(x)
        x = self.pool(x)

        return x

class back_model(torch.nn.Module):
    def __init__(self):
        super().__init__()

        model = resnet50()

        self.layer1 = model.layer1
        self.layer2 = model.layer2
        self.layer3 = model.layer3
        self.layer4 = model.layer4
        self.avgpool = model.avgpool
        self.flatten = torch.nn.Flatten()
        self.fc = model.fc

        for p in self.parameters():
            p.requires_grad = False
    
    def forward(self, x):
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.avgpool(x)
        x = self.flatten(x)
        x = self.fc(x)

        return x