
import argparse
import json
import os

import torch
import torch.nn as nn

from torch.utils.data import DataLoader, Dataset, random_split

from torchvision import datasets, transforms

from model import build_model, CLASS_NAMES, NUM_CLASSES



torch.manual_seed(42)

if torch.cuda.is_available():
    torch.cuda.manual_seed_all(42)



device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Using device:", device)



# Configuration

IMG_SIZE = 224
BATCH_SIZE = 32

MINORITY_CLASS_NAMES = [
    "CBSD",
    "CBB"
]



# TransformSubset

class TransformSubset(Dataset):

    def __init__(self, subset, transform):
        self.subset = subset
        self.transform = transform

    def __len__(self):
        return len(self.subset)

    def __getitem__(self, idx):

        image, label = self.subset[idx]

        if self.transform is not None:
            image = self.transform(image)

        return image, label



# Class-aware augmentation


class ClassAwareAugment:

    def __init__(
        self,
        base_transform,
        extra_transform,
        minority_label_ids
    ):

        self.base_transform = base_transform
        self.extra_transform = extra_transform
        self.minority_label_ids = set(minority_label_ids)

    def __call__(self, image, label):

        if label in self.minority_label_ids:
            image = self.extra_transform(image)

        image = self.base_transform(image)

        return image


class ClassAwareSubset(Dataset):

    def __init__(
        self,
        subset,
        class_aware_transform
    ):

        self.subset = subset
        self.class_aware_transform = class_aware_transform

    def __len__(self):
        return len(self.subset)

    def __getitem__(self, idx):

        image, label = self.subset[idx]

        image = self.class_aware_transform(
            image,
            label
        )

        return image, label



# normalization computation


def compute_normalization_stats(
    train_split,
    img_size=IMG_SIZE,
    batch_size=BATCH_SIZE
):

    print("\nCalculating normalization statistics...")

    plain_transform = transforms.Compose([
        transforms.Resize(
            (img_size, img_size)
        ),
        transforms.ToTensor()
    ])

    stats_dataset = TransformSubset(
        train_split,
        plain_transform
    )

    stats_loader = DataLoader(
        stats_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=2
    )

    channel_sum = torch.zeros(3)
    channel_sum_sq = torch.zeros(3)

    num_pixels = 0

    for images, _ in stats_loader:

        channel_sum += images.sum(
            dim=[0, 2, 3]
        )

        channel_sum_sq += (
            images ** 2
        ).sum(
            dim=[0, 2, 3]
        )

        num_pixels += (
            images.size(0)
            * images.size(2)
            * images.size(3)
        )

    mean = channel_sum / num_pixels

    variance = (
        channel_sum_sq / num_pixels
        - mean ** 2
    )

    std = variance.clamp(
        min=1e-8
    ).sqrt()

    mean = mean.tolist()
    std = std.tolist()

    print("Mean:", mean)
    print("Std :", std)

    return mean, std



# Build transforms


def build_transforms(mean, std):

    normalize = transforms.Normalize(
        mean=mean,
        std=std
    )

    # Training augmentation
    train_transform = transforms.Compose([

        transforms.Resize(
            (IMG_SIZE, IMG_SIZE)
        ),

        transforms.RandomHorizontalFlip(
            p=0.5
        ),

        transforms.RandomRotation(
            15
        ),

        transforms.RandomResizedCrop(
            IMG_SIZE,
            scale=(0.9, 1.0)
        ),

        transforms.ColorJitter(
            brightness=0.2,
            contrast=0.2,
            saturation=0.2,
            hue=0.05
        ),

        transforms.ToTensor(),

        normalize
    ])

    # Extra augmentation for minority classes
    minority_transform = transforms.Compose([

        transforms.RandomRotation(
            25
        ),

        transforms.ColorJitter(
            brightness=0.3,
            contrast=0.3,
            saturation=0.3,
            hue=0.08
        )
    ])

    # Validation/test transformation
    eval_transform = transforms.Compose([

        transforms.Resize(
            (IMG_SIZE, IMG_SIZE)
        ),

        transforms.ToTensor(),

        normalize
    ])

    return (
        train_transform,
        minority_transform,
        eval_transform
    )



# Build data loaders


def build_dataloaders(
    data_dir,
    checkpoint_dir
):

    print("\nLoading dataset...")

    base_dataset = datasets.ImageFolder(
        root=data_dir
    )

    print("Total images:", len(base_dataset))

    print(
        "class_to_idx:",
        base_dataset.class_to_idx
    )

   
    # Verify class order
 

    actual_classes = [
        name.replace(
            "Cassava___",
            ""
        )
        for name in base_dataset.classes
    ]

    print(
        "Dataset classes:",
        actual_classes
    )

    print(
        "Model classes:",
        CLASS_NAMES
    )
    expected_dataset_classes = [
    "bacterial_blight",
    "brown_streak_disease",
    "green_mottle",
    "healthy",
    "mosaic_disease"
]


    if actual_classes != expected_dataset_classes:

      raise ValueError(
          "\nUnexpected dataset class order!\n"
          f"Found:    {actual_classes}\n"
          f"Expected: {expected_dataset_classes}"
      )
    
    # 80 / 10 / 10 split

    train_size = int(
        0.80 * len(base_dataset)
    )

    val_size = int(
        0.10 * len(base_dataset)
    )

    test_size = (
        len(base_dataset)
        - train_size
        - val_size
    )

    generator = torch.Generator().manual_seed(42)

    train_split, val_split, test_split = random_split(
        base_dataset,
        [
            train_size,
            val_size,
            test_size
        ],
        generator=generator
    )

    print(
        f"\nTrain: {len(train_split)}"
        f"\nVal:   {len(val_split)}"
        f"\nTest:  {len(test_split)}"
    )

    
    # Normalization
    # --------------------------------------------------------
    mean, std = compute_normalization_stats(
        train_split
    )

    os.makedirs(
        checkpoint_dir,
        exist_ok=True
    )

    stats_path = os.path.join(
        checkpoint_dir,
        "normalization_stats.json"
    )

    with open(
        stats_path,
        "w"
    ) as f:

        json.dump(
            {
                "mean": mean,
                "std": std
            },
            f,
            indent=4
        )

    print(
        "\nSaved normalization statistics to:",
        stats_path
    )

   
    # Transforms

    (
        train_transform,
        minority_transform,
        eval_transform
    ) = build_transforms(
        mean,
        std
    )


    # Find minority class IDs
 
    minority_label_ids = []

    for class_name in base_dataset.classes:

        clean_name = class_name.replace(
            "Cassava___",
            ""
        )

        if clean_name in MINORITY_CLASS_NAMES:

            minority_label_ids.append(
                base_dataset.class_to_idx[
                    class_name
                ]
            )

    print(
        "Minority class IDs:",
        minority_label_ids
    )

   
    # Create datasets

    class_aware_transform = ClassAwareAugment(
        train_transform,
        minority_transform,
        minority_label_ids
    )

    train_dataset = ClassAwareSubset(
        train_split,
        class_aware_transform
    )

    val_dataset = TransformSubset(
        val_split,
        eval_transform
    )

    test_dataset = TransformSubset(
        test_split,
        eval_transform
    )

  
    # DataLoaders
  

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=2
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=2
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=2
    )

   
    # Class weights
    

    class_counts = torch.zeros(
        NUM_CLASSES
    )

    for idx in train_split.indices:

        _, label = base_dataset.samples[idx]

        class_counts[label] += 1

    print(
        "\nTrain class counts:",
        class_counts.tolist()
    )

    class_weights = (
        1.0
        / class_counts.clamp(min=1)
    )

    class_weights = (
        class_weights
        / class_weights.sum()
        * NUM_CLASSES
    )

    print(
        "Class weights:",
        class_weights.tolist()
    )

    return (
        train_loader,
        val_loader,
        test_loader,
        class_weights
    )



# Train one epoch


def train_one_epoch(
    model,
    loader,
    optimizer,
    criterion
):

    model.train()

    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in loader:

        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(images)

        loss = criterion(
            outputs,
            labels
        )

        loss.backward()

        optimizer.step()

        running_loss += (
            loss.item()
            * images.size(0)
        )

        correct += (
            outputs.argmax(1) == labels
        ).sum().item()

        total += labels.size(0)

    return (
        running_loss / total,
        correct / total
    )


# Validation/test evaluation

@torch.no_grad()
def evaluate(
    model,
    loader,
    criterion
):

    model.eval()

    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in loader:

        images = images.to(device)
        labels = labels.to(device)

        outputs = model(images)

        loss = criterion(
            outputs,
            labels
        )

        running_loss += (
            loss.item()
            * images.size(0)
        )

        correct += (
            outputs.argmax(1) == labels
        ).sum().item()

        total += labels.size(0)

    return (
        running_loss / total,
        correct / total
    )



# Main


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--data-dir",
        type=str,
        default="/content/cassava_dataset"
    )

    parser.add_argument(
        "--epochs",
        type=int,
        default=15
    )

    parser.add_argument(
        "--lr",
        type=float,
        default=1e-3
    )

    parser.add_argument(
        "--checkpoint-dir",
        type=str,
        default="/content/checkpoints"
    )

    args = parser.parse_args()

   
    # Check dataset
  

    if not os.path.isdir(
        args.data_dir
    ):

        raise FileNotFoundError(
            f"Dataset not found at "
            f"{args.data_dir}"
        )

    
    # Create checkpoint directory

    os.makedirs(
        args.checkpoint_dir,
        exist_ok=True
    )

   
    # Build loaders

    (
        train_loader,
        val_loader,
        test_loader,
        class_weights
    ) = build_dataloaders(
        args.data_dir,
        args.checkpoint_dir
    )

    # Build model
    

    model = build_model(
        num_classes=NUM_CLASSES
    ).to(device)

    print("\nModel:")
    print(model)

   
    # Loss

    criterion = nn.CrossEntropyLoss(
        weight=class_weights.to(device)
    )

   
    # Optimizer
   

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=args.lr
    )

  
    # Learning rate scheduler
   

    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode="min",
        patience=2,
        factor=0.5
    )

   
    # Training
  

    best_val_acc = 0.0

    best_checkpoint = os.path.join(
        args.checkpoint_dir,
        "best_model.pt"
    )

    for epoch in range(
        1,
        args.epochs + 1
    ):

        train_loss, train_acc = train_one_epoch(
            model,
            train_loader,
            optimizer,
            criterion
        )

        val_loss, val_acc = evaluate(
            model,
            val_loader,
            criterion
        )

        scheduler.step(
            val_loss
        )

        current_lr = optimizer.param_groups[0]["lr"]

        print(
            f"\nEpoch {epoch}/{args.epochs}"
            f" | train loss: {train_loss:.4f}"
            f" | train acc: {train_acc:.4f}"
            f" | val loss: {val_loss:.4f}"
            f" | val acc: {val_acc:.4f}"
            f" | lr: {current_lr:.6f}"
        )

        # Save best model
        if val_acc > best_val_acc:

            best_val_acc = val_acc

            torch.save(
                model.state_dict(),
                best_checkpoint
            )

            print(
                f"  ✓ New best model saved!"
                f" Validation accuracy: {val_acc:.4f}"
            )

  
   # best model before final test
    print(
        "\nLoading best model for final test..."
    )

    best_state = torch.load(
        best_checkpoint,
        map_location=device
    )

    model.load_state_dict(
        best_state
    )

    
    # Final test

    test_loss, test_acc = evaluate(
        model,
        test_loader,
        criterion
    )

    print(
        "\n========================================"
    )

    print(
        f"Best validation accuracy: "
        f"{best_val_acc:.4f}"
    )

    print(
        f"Final test loss: "
        f"{test_loss:.4f}"
    )

    print(
        f"Final test accuracy: "
        f"{test_acc:.4f}"
    )

    print(
        "========================================"
    )

    print(
        "\nCheckpoint saved at:"
    )

    print(
        best_checkpoint
    )


if __name__ == "__main__":
    main()
