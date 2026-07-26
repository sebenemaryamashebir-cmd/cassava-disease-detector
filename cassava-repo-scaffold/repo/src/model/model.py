"""
Custom CNN for Cassava Leaf Disease Detection — built and trained entirely from
scratch (no pretrained weights, no transfer learning), per project requirements.

Architecture style follows the course's CNN lab convention (03_cnn.ipynb):
named layer attributes (conv1, conv2, ...) + functional forward pass, so filters
and feature maps can be inspected the same way (e.g. model.conv1.weight,
forward hooks) as you did in that lab.

Classes: CBB, CBSD, CMD, Healthy  (4 classes)
Input:   224 x 224 RGB images  -- must match Member 1's preprocessing resize target
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

CLASS_NAMES = ["CBB", "CBSD", "CMD", "Healthy"]
NUM_CLASSES = len(CLASS_NAMES)


class CassavaCNN(nn.Module):
    """
    5 conv blocks (conv -> ReLU -> maxpool), each halving spatial size:
        224 -> 112 -> 56 -> 28 -> 14 -> 7
    then flatten -> FC -> dropout -> FC (raw logits, no softmax --
    nn.CrossEntropyLoss applies log-softmax internally, same as Lab 3's FFN).

    No BatchNorm (not used in the course's CNN lab) -- overfitting risk is
    managed instead with dropout + the augmentation Member 1 applies
    (rotation/flip/zoom), since there are no pretrained weights to fall back on.
    """

    def __init__(self, num_classes=NUM_CLASSES):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv4 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.conv5 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)

        self.dropout = nn.Dropout(0.3)
        self.fc1 = nn.Linear(256 * 7 * 7, 256)
        self.fc2 = nn.Linear(256, num_classes)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))   # 224 -> 112
        x = self.pool(F.relu(self.conv2(x)))   # 112 -> 56
        x = self.pool(F.relu(self.conv3(x)))   # 56  -> 28
        x = self.pool(F.relu(self.conv4(x)))   # 28  -> 14
        x = self.pool(F.relu(self.conv5(x)))   # 14  -> 7

        x = x.view(x.size(0), -1)              # flatten: [batch, 256*7*7]
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)                        # raw logits
        return x


def build_model(num_classes=NUM_CLASSES):
    return CassavaCNN(num_classes=num_classes)


if __name__ == "__main__":
    model = build_model()
    print(model)

    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"\nTotal params:     {total_params:,}")
    print(f"Trainable params: {trainable_params:,}")

    # By-hand check for fc1, same exercise as Lab 3 Part 2.2:
    #   input_dim * out_features + out_features (bias)
    fc1_by_hand = (256 * 7 * 7) * 256 + 256
    print(f"fc1 by-hand check: {fc1_by_hand:,} "
          f"(matches fc1: {sum(p.numel() for p in model.fc1.parameters()) == fc1_by_hand})")
