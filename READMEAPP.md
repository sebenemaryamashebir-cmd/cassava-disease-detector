# cassava-disease-detector
# Cassava Leaf Doctor

**FastAPI** (loads  teammate's PyTorch model + calls Gemini) → **React + Vite** frontend.

```
backend/    FastAPI app: /api/analyze takes a photo, returns diagnosis + recommendation
frontend/   React app, leaf-green theme
```


## 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
```

Edit `.env`:
- `MODEL_WEIGHTS_PATH` — should already point at `weights/cassava_model1.pt`
- `IMG_SIZE` — matches teammate's training size
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

## 2. Frontend

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
