from decouple import config

MODEL_WEIGHTS_PATH = config("MODEL_WEIGHTS_PATH", default="weights/cassava_model.pt")
IMG_SIZE = config("IMG_SIZE", default=224, cast=int)

GEMINI_API_KEY = config("GEMINI_API_KEY", default="")
GEMINI_MODEL = config("GEMINI_MODEL", default="gemini-flash-latest")

CORS_ORIGIN = config("CORS_ORIGIN", default="http://localhost:5173,http://127.0.0.1:5173")
CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGIN.split(",")]

# Standard 5-class label set used by the widely-known Kaggle "Cassava Leaf
# Disease Classification" competition. ASSUMPTION: if your teammate's model
# was trained on different classes or a different order, edit this list to
# match exactly — the order here must match the order used during training.
# Update your config CLASS_NAMES array to look exactly like this:
CLASS_NAMES = ['CBB', 'CBSD', 'CGM', 'Healthy', 'CMD']

