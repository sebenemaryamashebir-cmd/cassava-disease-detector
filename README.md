# Cassava Disease Detector

A deep learning system that classifies cassava leaf photos into one of five categories, paired with a full-stack web app (FastAPI + React) that lets users upload a photo and get an instant diagnosis plus an AI-generated, farmer-facing recommendation.

## What it does

1. A custom CNN (PyTorch) is trained on cassava leaf images to classify them into:
   - **CBB** — Cassava Bacterial Blight
   - **CBSD** — Cassava Brown Streak Disease
   - **CGM** — Cassava Green Mottle / Mite damage
   - **CMD** — Cassava Mosaic Disease
   - **Healthy**
2. A **FastAPI** backend loads the trained model, runs inference on an uploaded photo, and calls the **Gemini API** to turn the raw prediction into a plain-language recommendation for a farmer.
3. A **React + Vite** frontend (leaf-green theme) provides the upload UI and displays the diagnosis + recommendation.

## Repository structure

```
.
├── backend/              FastAPI app — /api/analyze takes a photo, returns diagnosis + recommendation
├── frontend/             React + Vite app, leaf-green theme
├── model.py              CNN architecture definition (CassavaCNN)
├── train.py              Training script (data loading, augmentation, training loop)
├── evaluate.py           Evaluation / metrics script
├── requirements.txt      Python dependencies for training/evaluation
└── .gitignore
```

## Model architecture

`CassavaCNN` (defined in `model.py`) is a 5-layer convolutional network:

- 5× `Conv2d → BatchNorm → ReLU → MaxPool` blocks (channels: 3→16→32→64→128→256)
- Input images are resized to **224×224**, giving a 7×7×256 feature map after pooling
- A dropout (0.3) + fully-connected head (256 → 5 classes)

```python
NUM_CLASSES = 5
CLASS_NAMES = ['CBB', 'CBSD', 'CGM', 'Healthy', 'CMD']
```

## Training (`train.py`)

- Expects an `ImageFolder`-style dataset directory with class subfolders named:
  `bacterial_blight`, `brown_streak_disease`, `green_mottle`, `healthy`, `mosaic_disease`
- Splits data **80% train / 10% val / 10% test** (seeded for reproducibility)
- Computes dataset mean/std for normalization and saves them to `normalization_stats.json` in the checkpoint directory
- Applies standard augmentation (flip, rotation, resized crop, color jitter) plus **extra augmentation for the minority classes** (`CBSD`, `CBB`) to help with class imbalance
- Uses class-weighted `CrossEntropyLoss`, Adam optimizer, and a `ReduceLROnPlateau` scheduler
- Saves the best-performing model (by validation accuracy) as `best_model.pt`

Example run:

```bash
pip install -r requirements.txt

python train.py \
  --data-dir /path/to/cassava_dataset \
  --epochs 15 \
  --lr 1e-3 \
  --checkpoint-dir /path/to/checkpoints
```

## Evaluation (`evaluate.py`)

Loads a trained checkpoint and computes metrics (accuracy, confusion matrix, etc.) on a held-out test set.

## Web app (backend + frontend)

The `backend/` and `frontend/` folders make up the deployable app that wraps the trained model.

### Model weights

The backend loads the trained weights from `backend/weights/`, in either of two formats:

- **TorchScript** (`torch.jit.save(...)`) — self-contained.
- **State dict** (`torch.save(model.state_dict(), ...)`) — paired with the `CassavaCNN` class in `backend/app/model_def/architecture.py`.

The backend's `IMG_SIZE` (set via `.env`) matches the size the model was trained at — `224` in this repo — and `CLASS_NAMES` in `backend/app/config.py` matches the exact class order the model was trained with (`CBB, CBSD, CGM, CMD, Healthy`), since a mismatch here silently mislabels every prediction rather than causing a crash.

### Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
```

`.env` variables:

| Variable              | Purpose                                                                 |
|-----------------------|--------------------------------------------------------------------------|
| `MODEL_WEIGHTS_PATH`  | Path to the weights file (default `weights/cassava_model.pt`)           |
| `IMG_SIZE`             | Matches the size the model was trained at                               |
| `GEMINI_API_KEY`       | Key from https://aistudio.google.com/apikey                             |
| `GEMINI_MODEL`         | Defaults to `gemini-flash-latest`                                       |

Run the server:

```bash
uvicorn app.main:app --reload --port 8000
```

`http://127.0.0.1:8000/api/health` returns `{"status":"ok"}` once the model loads successfully.

### Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The app runs at `http://localhost:5173` — upload a leaf photo and hit **Analyze**.

## How a request flows

1. The React app sends the image as `multipart/form-data` to `POST /api/analyze`.
2. FastAPI preprocesses it (resize + normalize) and runs it through the PyTorch model.
3. The predicted class + confidence are sent to Gemini with a prompt asking for a farmer-facing recommendation.
4. Both the raw prediction and the recommendation are returned in a single response. If Gemini fails (bad key, rate limit, etc.), the diagnosis still shows — a `recommendation_error` field is set instead of `recommendation`, and the UI surfaces that separately rather than failing the whole request.

## Known gaps / roadmap

- No confidence threshold or "inconclusive" state — a top prediction is always shown even at low confidence (the recommendation text mentions low confidence, but the UI doesn't visually flag it yet).
- No history of past scans.
- `weights/` and `.env` stay untracked via `.gitignore`.

## Requirements

```
torch>=2.2
torchvision>=0.17
numpy
pandas
matplotlib
scikit-learn
Pillow
fastapi
uvicorn[standard]
python-multipart
pydantic
```

## Team 

- Sebenemaryam Ashebir Asnake
- Jedidiah Klenam Dogbey 
- Tracy-Phyron Jinor

## License

No license specified yet.
