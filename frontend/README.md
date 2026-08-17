# CassavaCare — Frontend Redesign

Redesign of the cassava leaf disease detector frontend into a dashboard-style
agricultural AI product, built to the spec in `CassavaCare_Frontend_Redesign_Prompt.pdf`.

## What changed vs. the original

- Two-panel form → full app shell: dark forest-green sidebar, page header, card-based layout.
- Added pages: **Dashboard** (overview), **Disease Detection** (the original flow, redesigned),
  **Prediction History** (local, via `localStorage`), **Crop Guide**, **About**.
- Redesigned upload flow, image preview, circular confidence gauge, animated probability bars,
  polished empty/loading/error states, and an "Understanding the Prediction" explainability
  placeholder ready for a future Grad-CAM image.
- Component architecture split into `Layout/`, `Dashboard/`, `Detection/`, `Results/`,
  `History/`, `CropGuide/`, `About/`, `Common/`.

## What did NOT change

- `src/api.js` — same `baseURL: http://127.0.0.1:8001/api/`.
- The `POST /api/analyze` request: still sends `file` as `multipart/form-data`.
- The response fields consumed: `predicted_class`, `confidence`, `probabilities`,
  `recommendation`, `recommendation_error`.

If your backend ever adds a Grad-CAM URL to the response, pass it as
`result.gradcam_url` — `ExplainabilityCard` already knows how to render it.

## Running it

```bash
npm install
npm run dev      # starts on http://localhost:5173
```

Make sure your FastAPI backend is running on `127.0.0.1:8001` first (or update
`src/api.js` if it's somewhere else).

## Notes / things you might want to change next

- Prediction history is local-only (`src/lib/history.js`). If you build a real
  history endpoint later, that's the only file that needs to change.
- Crop Guide copy (`src/lib/diseaseInfo.js`) is general background info, not
  treatment advice — worth reviewing with whoever's checking the project for
  accuracy before you present it.
- Colors, spacing, and radii are all CSS variables at the top of
  `src/styles/theme.css` if you want to tweak the palette.
