# Cassava Leaf Disease Detector

A group project that classifies cassava leaf images into one of four classes —
**CBB** (Cassava Bacterial Blight), **CBSD** (Cassava Brown Streak Disease),
**CMD** (Cassava Mosaic Disease), and **Healthy** — using a convolutional
neural network **built and trained entirely from scratch** (no pretrained
weights / no transfer learning, per project requirements).

The system covers the full pipeline: data preprocessing → CNN training →
evaluation → FastAPI backend → frontend + LLM-assisted explanation.

## Team

| Member | Responsibility |
|---|---|
| Member 1 | Data collection & preprocessing |
| Member 2 | CNN architecture & training |
| Member 3 | Evaluation & optimization |
| Member 4 | Deployment & integration |

## Project structure

```
cassava-disease-detector/
├── data/
│   ├── raw/            # original Kaggle dataset (gitignored)
│   └── processed/      # cleaned/split/augmented data (gitignored)
├── notebooks/          # EDA and experiments
├── src/
│   ├── preprocessing/  # Member 1 — cleaning, splitting, augmentation
│   ├── model/          # Member 2 — CNN architecture, training loop
│   ├── evaluation/      # Member 3 — metrics, confusion matrix, plots
│   └── api/              # Member 4 — FastAPI backend
├── frontend/           # Member 4 — upload UI
├── docs/                 # architecture diagrams, report drafts
├── tests/
├── requirements.txt
└── README.md
```

## Setup

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Model

`src/model/model.py` — a custom CNN (5 conv blocks, batch norm, dropout,
global average pooling) sized for a small from-scratch training run.

Sanity-check the architecture with dummy data (no dataset needed):

```bash
cd src/model
python test_model_dummy.py
```

## Branching workflow

- `main` — always stable/working
- `feature/preprocessing`, `feature/cnn-model`, `feature/evaluation`, `feature/api-deploy`
  — one branch per member's area
- Open a PR into `main`; at least one teammate reviews before merging

## Status

Week 10–11 in progress — see project timeline doc for the full week-by-week plan.
