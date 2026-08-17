

import argparse
import os

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset, random_split
from torchvision import datasets, transforms

from model import build_model, CLASS_NAMES, NUM_CLASSES

torch.manual_seed(42)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

IMG_SIZE = 224
BATCH_SIZE = 32  # matches Member 1's DataLoader batch size

# Same augmentation choices as Member 1's notebook (cell 28) -- applied to
# train only. Val/test get resize + tensor only, no augmentation, so
# evaluation reflects real, undistorted images.
train_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(15),
    transforms.RandomResizedCrop(IMG_SIZE, scale=(0.9, 1.0)),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05),
    transforms.ToTensor(),
])

eval_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
])


class TransformSubset(Dataset):
    """
    Wraps a torch Subset (a split of indices into the base ImageFolder) and
    applies a chosen transform on __getitem__. This is what makes it possible
    to split ONCE, then give train/val/test each their own transform, instead
    of re-loading the whole dataset per split like the notebook did.
    """

    def __init__(self, subset, transform):
        self.subset = subset
        self.transform = transform

    def __len__(self):
        return len(self.subset)

    def __getitem__(self, idx):
        image, label = self.subset[idx]  # base ImageFolder returns a PIL image here
        if self.transform is not None:
            image = self.transform(image)
        return image, label


def build_dataloaders(data_dir, batch_size=BATCH_SIZE):
    # No transform here on purpose -- we split on the raw dataset first,
    # then apply per-split transforms below. This is the key fix.
    base_dataset = datasets.ImageFolder(root=data_dir)
    print("Total images:", len(base_dataset))
    print("class_to_idx:", base_dataset.class_to_idx)

    # Sanity check: make sure CLASS_NAMES in model.py still lines up with
    # whatever ImageFolder assigns on this machine (alphabetical by folder name).
    expected_order = [name.replace("Cassava___", "") for name in sorted(base_dataset.classes)]
    print("model.py CLASS_NAMES:", CLASS_NAMES)
    print("ImageFolder order:   ", expected_order)

    train_size = int(0.80 * len(base_dataset))
    val_size = int(0.10 * len(base_dataset))
    test_size = len(base_dataset) - train_size - val_size

    generator = torch.Generator().manual_seed(42)  # same seed as the notebook
    train_split, val_split, test_split = random_split(
        base_dataset, [train_size, val_size, test_size], generator=generator
    )
    print(f"Train: {len(train_split)}  Val: {len(val_split)}  Test: {len(test_split)}")

    train_dataset = TransformSubset(train_split, train_transform)
    val_dataset = TransformSubset(val_split, eval_transform)
    test_dataset = TransformSubset(test_split, eval_transform)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=2)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=2)

    # Class weights for the loss, computed from the TRAIN split only (not the
    # full dataset) -- avoids leaking val/test distribution into training.
    class_counts = torch.zeros(NUM_CLASSES)
    for idx in train_split.indices:
        _, label = base_dataset.samples[idx]
        class_counts[label] += 1
    print("Train class counts:", class_counts.tolist())

    class_weights = 1.0 / class_counts.clamp(min=1)
    class_weights = class_weights / class_weights.sum() * NUM_CLASSES  # normalize

    return train_loader, val_loader, test_loader, class_weights


def train_one_epoch(model, loader, optimizer, criterion):
    model.train()
    running_loss, correct, total = 0.0, 0, 0
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)
        correct += (outputs.argmax(1) == labels).sum().item()
        total += labels.size(0)
    return running_loss / total, correct / total


@torch.no_grad()
def evaluate(model, loader, criterion):
    model.eval()
    running_loss, correct, total = 0.0, 0, 0
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        loss = criterion(outputs, labels)
        running_loss += loss.item() * images.size(0)
        correct += (outputs.argmax(1) == labels).sum().item()
        total += labels.size(0)
    return running_loss / total, correct / total


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=str, default="/content/cassava_dataset",
                         help="Path to the extracted dataset (same layout as Member 1's notebook)")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--checkpoint-dir", type=str, default="checkpoints")
    args = parser.parse_args()

    if not os.path.isdir(args.data_dir):
        raise FileNotFoundError(
            f"Dataset not found at {args.data_dir}. "
            f"Pass --data-dir pointing at the extracted cassava_dataset folder."
        )

    os.makedirs(args.checkpoint_dir, exist_ok=True)

    train_loader, val_loader, test_loader, class_weights = build_dataloaders(args.data_dir)

    model = build_model().to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights.to(device))
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    best_val_acc = 0.0
    for epoch in range(1, args.epochs + 1):
        tr_loss, tr_acc = train_one_epoch(model, train_loader, optimizer, criterion)
        va_loss, va_acc = evaluate(model, val_loader, criterion)

        print(f"Epoch {epoch}/{args.epochs} | "
              f"train loss {tr_loss:.3f} acc {tr_acc:.3f} | "
              f"val loss {va_loss:.3f} acc {va_acc:.3f}")

        if va_acc > best_val_acc:
            best_val_acc = va_acc
            ckpt_path = os.path.join(args.checkpoint_dir, "best_model.pt")
            torch.save(model.state_dict(), ckpt_path)
            print(f"  -> New best val acc ({va_acc:.3f}), saved to {ckpt_path}")

    # Final test-set evaluation (only run once, at the very end)
    test_loss, test_acc = evaluate(model, test_loader, criterion)
    print(f"\nFinal test loss {test_loss:.3f} | test acc {test_acc:.3f}")


if __name__ == "__main__":
    main()
