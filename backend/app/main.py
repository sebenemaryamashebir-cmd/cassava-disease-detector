import io
from dotenv import load_dotenv 
load_dotenv() 
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

from . import config, model_service, gemini_service

app = FastAPI(title="Cassava Leaf Disease Detector")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    model_service.load_model()


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file.")

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
    except Exception:
        raise HTTPException(status_code=400, detail="Couldn't read that image — try a different file.")

    try:
        prediction = model_service.predict(image)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model prediction failed: {e}")

    try:
        recommendation = gemini_service.get_recommendation(
            prediction["predicted_class"], prediction["confidence"]
        )
    except Exception as e:
        # Prediction still succeeded  surface the Gemini failure separately
        # instead of failing the whole request, so the UI can still show the CNN result.
        recommendation = None
        prediction["recommendation_error"] = str(e)

    return {**prediction, "recommendation": recommendation}
