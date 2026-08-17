import torch
import torch.nn as nn
import torch.nn.functional as F

NUM_CLASSES = 5
CLASS_NAMES = ['CBB', 'CBSD', 'CGM', 'Healthy', 'CMD']

class CassavaCNN(nn.Module):
    def __init__(self, num_classes=NUM_CLASSES):
        super().__init__()
        # Layer 1
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(16) 

        # Layer 2
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(32)

        # Layer 3
        self.conv3 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(64)

        # Layer 4
        self.conv4 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn4 = nn.BatchNorm2d(128)

        # Layer 5
        self.conv5 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
        self.bn5 = nn.BatchNorm2d(256)

        self.pool = nn.MaxPool2d(2, 2)
        self.dropout = nn.Dropout(0.3)

        # Linear Layers
        self.fc1 = nn.Linear(256 * 7 * 7, 256)
        self.fc2 = nn.Linear(256, num_classes)

    def forward(self, x):
        # Forward pass applying Conv, BatchNorm ,ReLU and Pool
        x = self.pool(F.relu(self.bn1(self.conv1(x))))   # 224 -> 112
        x = self.pool(F.relu(self.bn2(self.conv2(x))))   # 112 -> 56
        x = self.pool(F.relu(self.bn3(self.conv3(x))))   # 56  -> 28
        x = self.pool(F.relu(self.bn4(self.conv4(x))))   # 28  -> 14
        x = self.pool(F.relu(self.bn5(self.conv5(x))))   # 14  -> 7

        x = x.view(x.size(0), -1)                      
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)                               
        return x

def build_model(num_classes=NUM_CLASSES):
    return CassavaCNN(num_classes=num_classes)
