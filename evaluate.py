
import argparse
import json
import os

import numpy as np
import torch

from torch.utils.data import DataLoader, Dataset, random_split

from torchvision import datasets, transforms

from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix
)

import matplotlib.pyplot as plt
import seaborn as sns

from model import build_model, CLASS_NAMES, NUM_CLASSES



# Device

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Using device:", device)



# Configuration


IMG_SIZE = 224
BATCH_SIZE = 32



# Dataset Model Class Mapping



DATASET_TO_MODEL_CLASS = {
    "bacterial_blight": "CBB",
    "brown_streak_disease": "CBSD",
    "green_mottle": "CGM",
    "healthy": "Healthy",
    "mosaic_disease": "CMD"
}



# TransformSubset

class TransformSubset(Dataset):

    def __init__(
        self,
        subset,
        transform
    ):

        self.subset = subset
        self.transform = transform

    def __len__(self):

        return len(self.subset)

    def __getitem__(self, idx):

        image, label = self.subset[idx]

        if self.transform is not None:
            image = self.transform(image)

        return image, label



# normalization


def load_eval_transform(
    checkpoint_dir
):

    stats_path = os.path.join(
        checkpoint_dir,
        "normalization_stats.json"
    )

    if not os.path.exists(
        stats_path
    ):

        raise FileNotFoundError(
            "\nNormalization statistics were not found.\n"
            f"Expected:\n{stats_path}\n\n"
            "This usually means the model has not been trained "
            "with the new train.py yet.\n"
            "Run train.py first."
        )

    with open(
        stats_path,
        "r"
    ) as f:

        stats = json.load(f)

    mean = stats["mean"]
    std = stats["std"]

    print(
        "\nLoaded normalization statistics:"
    )

    print(
        "Mean:",
        mean
    )

    print(
        "Std:",
        std
    )

    normalize = transforms.Normalize(
        mean=mean,
        std=std
    )

    transform = transforms.Compose([

        transforms.Resize(
            (IMG_SIZE, IMG_SIZE)
        ),

        transforms.ToTensor(),

        normalize
    ])

    return transform



# Build test loader


def build_test_loader(
    data_dir,
    eval_transform
):

    base_dataset = datasets.ImageFolder(
        root=data_dir
    )

   
    # Classes found by ImageFolder
 

    dataset_classes = [
        name.replace(
            "Cassava___",
            ""
        )
        for name in base_dataset.classes
    ]

    print(
        "\nClasses found on disk:",
        dataset_classes
    )

  
    # Convert dataset names to model names

    mapped_classes = []

    for name in dataset_classes:

        if name not in DATASET_TO_MODEL_CLASS:

            raise ValueError(
                "\nUNKNOWN DATASET CLASS!\n"
                f"Found: {name}\n"
                f"Known classes: "
                f"{list(DATASET_TO_MODEL_CLASS.keys())}"
            )

        mapped_classes.append(
            DATASET_TO_MODEL_CLASS[name]
        )

    print(
        "Mapped classes:",
        mapped_classes
    )

    print(
        "Expected classes:",
        CLASS_NAMES
    )

   
    # Check class order

    if mapped_classes != CLASS_NAMES:

        raise ValueError(
            "\nCLASS ORDER MISMATCH!\n"
            f"Dataset folders: {dataset_classes}\n"
            f"Mapped classes:  {mapped_classes}\n"
            f"Model classes:   {CLASS_NAMES}\n\n"
            "The dataset class order must match the model "
            "output order."
        )

   
    # Number of classes

    num_classes = len(
        dataset_classes
    )

    if num_classes != NUM_CLASSES:

        raise ValueError(
            f"Expected {NUM_CLASSES} classes "
            f"but found {num_classes}."
        )

   
    # SAME 80/10/10 split as training

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

    _, _, test_split = random_split(

        base_dataset,

        [
            train_size,
            val_size,
            test_size
        ],

        generator=generator
    )

    test_dataset = TransformSubset(
        test_split,
        eval_transform
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=2
    )

    print(
        "Test set size:",
        len(test_split)
    )

    return (
        test_loader,
        mapped_classes,
        num_classes
    )



# Inference


@torch.no_grad()
def run_inference(
    model,
    loader
):

    model.eval()

    all_preds = []
    all_labels = []
    all_probs = []

    for images, labels in loader:

        images = images.to(
            device
        )

        outputs = model(
            images
        )

        probabilities = torch.softmax(
            outputs,
            dim=1
        )

        predictions = outputs.argmax(
            dim=1
        )

        all_preds.append(
            predictions.cpu().numpy()
        )

        all_labels.append(
            labels.numpy()
        )

        all_probs.append(
            probabilities.cpu().numpy()
        )

    return (
        np.concatenate(all_preds),
        np.concatenate(all_labels),
        np.concatenate(all_probs)
    )



# Metrics

def compute_metrics(
    y_true,
    y_pred,
    class_names
):

    accuracy = accuracy_score(
        y_true,
        y_pred
    )

    precision, recall, f1, support = (
        precision_recall_fscore_support(

            y_true,
            y_pred,

            labels=range(
                len(class_names)
            ),

            zero_division=0
        )
    )

    precision_macro, recall_macro, f1_macro, _ = (
        precision_recall_fscore_support(

            y_true,
            y_pred,

            average="macro",

            zero_division=0
        )
    )

    precision_weighted, recall_weighted, f1_weighted, _ = (
        precision_recall_fscore_support(

            y_true,
            y_pred,

            average="weighted",

            zero_division=0
        )
    )

    return {

        "accuracy": accuracy,

        "per_class": {

            class_names[i]: {

                "precision": precision[i],

                "recall": recall[i],

                "f1": f1[i],

                "support": int(
                    support[i]
                )

            }

            for i in range(
                len(class_names)
            )
        },

        "macro": {

            "precision": precision_macro,

            "recall": recall_macro,

            "f1": f1_macro

        },

        "weighted": {

            "precision": precision_weighted,

            "recall": recall_weighted,

            "f1": f1_weighted

        }
    }



# Print metrics

def print_metrics(
    metrics
):

    print(
        "\n========================================"
    )

    print(
        f"Overall accuracy: "
        f"{metrics['accuracy']:.4f}"
    )

    print(
        "========================================\n"
    )

    print(
        f"{'Class':<20}"
        f"{'Precision':>10}"
        f"{'Recall':>10}"
        f"{'F1':>10}"
        f"{'Support':>10}"
    )

    print(
        "-" * 60
    )

    for cls, values in metrics[
        "per_class"
    ].items():

        print(
            f"{cls:<20}"
            f"{values['precision']:>10.3f}"
            f"{values['recall']:>10.3f}"
            f"{values['f1']:>10.3f}"
            f"{values['support']:>10d}"
        )

    print(
        "\nMacro average:"
    )

    print(
        f"Precision: "
        f"{metrics['macro']['precision']:.3f}"
    )

    print(
        f"Recall: "
        f"{metrics['macro']['recall']:.3f}"
    )

    print(
        f"F1: "
        f"{metrics['macro']['f1']:.3f}"
    )

    print(
        "\nWeighted average:"
    )

    print(
        f"Precision: "
        f"{metrics['weighted']['precision']:.3f}"
    )

    print(
        f"Recall: "
        f"{metrics['weighted']['recall']:.3f}"
    )

    print(
        f"F1: "
        f"{metrics['weighted']['f1']:.3f}"
    )



# Confusion matrix


def plot_confusion_matrix(
    y_true,
    y_pred,
    class_names,
    out_path
):

    cm = confusion_matrix(
        y_true,
        y_pred,
        labels=range(
            len(class_names)
        )
    )

    plt.figure(
        figsize=(8, 6)
    )

    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=class_names,
        yticklabels=class_names
    )

    plt.xlabel(
        "Predicted label"
    )

    plt.ylabel(
        "True label"
    )

    plt.title(
        "Confusion Matrix — Test Set"
    )

    plt.tight_layout()

    plt.savefig(
        out_path,
        dpi=150
    )

    plt.close()

    print(
        "\nConfusion matrix saved to:"
    )

    print(
        out_path
    )

    return cm



# Main


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--data-dir",
        type=str,
        default="/content/cassava_dataset"
    )

    parser.add_argument(
        "--checkpoint",
        type=str,
        default="/content/checkpoints/best_model.pt"
    )

    parser.add_argument(
        "--out-dir",
        type=str,
        default="/content/eval_results"
    )

    args = parser.parse_args()

    # Check files
   

    if not os.path.exists(
        args.checkpoint
    ):

        raise FileNotFoundError(
            f"\nCheckpoint not found:\n"
            f"{args.checkpoint}\n\n"
            "Run train.py first."
        )

    if not os.path.isdir(
        args.data_dir
    ):

        raise FileNotFoundError(
            f"\nDataset not found:\n"
            f"{args.data_dir}"
        )

    os.makedirs(
        args.out_dir,
        exist_ok=True
    )

   
    # normalization
   

    checkpoint_dir = os.path.dirname(
        args.checkpoint
    )

    eval_transform = load_eval_transform(
        checkpoint_dir
    )

  
    # Build test loader
   

    (
        test_loader,
        class_names,
        num_classes
    ) = build_test_loader(
        args.data_dir,
        eval_transform
    )

   
    # build same model
   

    model = build_model(
        num_classes=num_classes
    ).to(device)

  
    # Load checkpoint


    print(
        "\nLoading checkpoint:"
    )

    print(
        args.checkpoint
    )

    state_dict = torch.load(
        args.checkpoint,
        map_location=device
    )

    # state_dict checkpoint
    if isinstance(
        state_dict,
        dict
    ) and "model_state_dict" in state_dict:

        state_dict = state_dict[
            "model_state_dict"
        ]

    model.load_state_dict(
        state_dict
    )

    print(
        "✓ Checkpoint loaded successfully."
    )

   
    # Run inference
  

    print(
        "\nRunning inference..."
    )

    y_pred, y_true, probabilities = (
        run_inference(
            model,
            test_loader
        )
    )

  
    # Metrics
   

    metrics = compute_metrics(
        y_true,
        y_pred,
        class_names
    )

    print_metrics(
        metrics
    )

   
    # Confusion matrix
   

    confusion_path = os.path.join(
        args.out_dir,
        "confusion_matrix.png"
    )

    cm = plot_confusion_matrix(
        y_true,
        y_pred,
        class_names,
        confusion_path
    )

    print(
        "\nRaw confusion matrix:"
    )

    print(
        cm
    )

  
    # Classification report
   

    report = classification_report(

        y_true,
        y_pred,

        labels=range(
            num_classes
        ),

        target_names=class_names,

        zero_division=0
    )

    report_path = os.path.join(
        args.out_dir,
        "classification_report.txt"
    )

    with open(
        report_path,
        "w"
    ) as f:

        f.write(
            f"Checkpoint: "
            f"{args.checkpoint}\n\n"
        )

        f.write(
            f"Overall accuracy: "
            f"{metrics['accuracy']:.4f}\n\n"
        )

        f.write(
            report
        )

    print(
        "\nClassification report saved to:"
    )

    print(
        report_path
    )


if __name__ == "__main__":
    main()
