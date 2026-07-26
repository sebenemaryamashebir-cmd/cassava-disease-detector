"""
Sanity-check the CassavaCNN architecture using DUMMY (random) data -- same
train_one_epoch/evaluate pattern as the course's CNN lab, but with random
tensors so Member 2 can confirm the model works before Member 1's real
preprocessed dataset is ready.

Run:  python test_model_dummy.py
"""

import torch
import torch.nn as nn

from model import build_model, CLASS_NAMES, NUM_CLASSES

torch.manual_seed(0)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

BATCH_SIZE = 8
IMG_SIZE = 224  # <-- must match Member 1's preprocessing resize target


def make_dummy_loader(num_batches=3):
    """A tiny in-memory stand-in for a real DataLoader."""
    batches = []
    for _ in range(num_batches):
        images = torch.randn(BATCH_SIZE, 3, IMG_SIZE, IMG_SIZE)
        labels = torch.randint(0, NUM_CLASSES, (BATCH_SIZE,))
        batches.append((images, labels))
    return batches


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
    model = build_model().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    train_loader = make_dummy_loader(num_batches=3)
    val_loader = make_dummy_loader(num_batches=1)

    print(f"\nInput shape per batch: [{BATCH_SIZE}, 3, {IMG_SIZE}, {IMG_SIZE}]")

    tr_loss, tr_acc = train_one_epoch(model, train_loader, optimizer, criterion)
    va_loss, va_acc = evaluate(model, val_loader, criterion)

    print(f"train loss {tr_loss:.3f} acc {tr_acc:.3f} | "
          f"val loss {va_loss:.3f} acc {va_acc:.3f}")
    print(f"(Loss should be near ln({NUM_CLASSES}) ≈ "
          f"{torch.log(torch.tensor(float(NUM_CLASSES))):.2f} on random data/labels "
          f"-- there's nothing real to learn yet, this just proves the wiring works.)")

    # Confirm every parameter gets a gradient (nothing disconnected in the graph)
    missing_grad = [name for name, p in model.named_parameters() if p.grad is None]
    if missing_grad:
        print(f"WARNING: these params got no gradient: {missing_grad}")
    else:
        print("All parameters received gradients -- backward pass OK.")

    print("\n✅ Model architecture is wired correctly and ready for real data.")


if __name__ == "__main__":
    main()
