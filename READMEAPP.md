# cassava-disease-detector
# Cassava Leaf Doctor

**FastAPI** (loads your teammate's PyTorch model + calls Gemini) → **React + Vite** frontend.

```
backend/    FastAPI app: /api/analyze takes a photo, returns diagnosis + recommendation
frontend/   React app, leaf-green theme
```

## 1. Get the model file from your teammate

Two ways they might have saved it — ask which one:

- **TorchScript** (`torch.jit.save(...)`) — best case, it's self-contained.
- **State dict** (`torch.save(model.state_dict(), ...)`) — you'll also need their
  exact model class. Copy it into `backend/app/model_def/architecture.py`,
  replacing the placeholder `CassavaModel` there.

Either way, drop the weights file into `backend/weights/` (see the note file
already in that folder).

**Also ask your teammate:**
- What image size did they train at (224? 380?) — set `IMG_SIZE` in `.env` to match.
- What are the class names, and in what order? The placeholder in
  `backend/app/config.py` (`CLASS_NAMES`) assumes the standard 5-class Kaggle
  cassava set (CBB, CBSD, CGM, CMD, Healthy) — if theirs differs, edit that list
  to match the exact order their model was trained with. Getting this wrong
  won't crash anything, it'll just silently mislabel every prediction.

## 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
```

Edit `.env`:
- `MODEL_WEIGHTS_PATH` — should already point at `weights/cassava_model.pt`, rename to match your actual file
- `IMG_SIZE` — match your teammate's training size
- `GEMINI_API_KEY` — get one free at https://aistudio.google.com/apikey
- `GEMINI_MODEL` — defaults to `gemini-flash-latest`; check
  https://ai.google.dev/gemini-api/docs/models if it errors, since Google
  periodically retires older dated model names

Run it:
```bash
uvicorn app.main:app --reload --port 8000
```

Check `http://127.0.0.1:8000/api/health` — should return `{"status":"ok"}`. If it
fails to start, the error will usually be the model file not being found, or the
architecture not matching the state_dict.

## 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`, upload a leaf photo, hit Analyze.

## How a request flows

1. React sends the image as `multipart/form-data` to `POST /api/analyze`
2. FastAPI preprocesses it (resize + normalize) and runs it through the PyTorch model
3. The predicted class + confidence get sent to Gemini with a prompt asking for a
   farmer-facing recommendation
4. Both the raw prediction and the recommendation come back in one response

If Gemini fails (bad API key, rate limit, etc.) the diagnosis still shows —
`recommendation_error` gets set instead of `recommendation`, and the UI surfaces
that separately rather than failing the whole request.

## Known gaps to build next

- No confidence threshold / "inconclusive" state — currently always shows a
  top prediction even at low confidence (the recommendation text does mention
  low confidence, but the UI doesn't visually flag it)
- No history of past scans
- `weights/` and `.env` are meant to stay untracked if you put this in git —
  add a `.gitignore` with those before pushing
