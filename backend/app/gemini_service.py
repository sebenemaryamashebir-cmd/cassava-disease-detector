import google.generativeai as genai
from . import config

_configured = False


def _ensure_configured():
    global _configured
    if not _configured:
        if not config.GEMINI_API_KEY or config.GEMINI_API_KEY == "your_gemini_api_key_here":
            raise RuntimeError("GEMINI_API_KEY is not set — add it to backend/.env")
        genai.configure(api_key=config.GEMINI_API_KEY)
        _configured = True


def get_recommendation(predicted_class: str, confidence: float) -> str:
    """Asks Gemini for a short, practical recommendation based on the CNN's prediction.
    Confidence is passed in so the model can hedge appropriately on uncertain calls."""
    _ensure_configured()

    model = genai.GenerativeModel(config.GEMINI_MODEL)

    prompt = f"""You are an agricultural extension assistant helping a cassava farmer
in Ghana interpret a leaf-disease scan from a computer vision model.

Model prediction: {predicted_class}
Model confidence: {confidence}%

Write a short, practical response (under 150 words) with:
1. A one-sentence plain-language explanation of what this diagnosis means.
2. 2-4 concrete next steps the farmer should take.
3. If confidence is below 70%, note that they should confirm with a local
   agricultural extension officer before acting.

Keep it plain and actionable — no headers, no markdown, just clear prose."""

    response = model.generate_content(prompt)
    return response.text.strip()
