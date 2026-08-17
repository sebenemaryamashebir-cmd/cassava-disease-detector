import os
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms

from . import config

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


_TRANSFORM = transforms.Compose(
    [
        transforms.Resize((config.IMG_SIZE, config.IMG_SIZE)),
        transforms.ToTensor(),
       
    ]
)

_model = None


def load_model():
    """Loads once at server startup. Tries TorchScript first (self-contained,
    no architecture file needed); falls back to state_dict + CassavaModel."""
    global _model

    if not os.path.exists(config.MODEL_WEIGHTS_PATH):
        raise FileNotFoundError(
            f"Model weights not found at '{config.MODEL_WEIGHTS_PATH}'. "
            "Ask your teammate for the trained .pt/.pth file and place it there, "
            "or update MODEL_WEIGHTS_PATH in .env."
        )

    try:
        _model = torch.jit.load(config.MODEL_WEIGHTS_PATH, map_location=device)
        print("Loaded model as TorchScript.")
    except RuntimeError:
        from .model_def.architecture import CassavaModel

        _model = CassavaModel(num_classes=len(config.CLASS_NAMES))
        state_dict = torch.load(config.MODEL_WEIGHTS_PATH, map_location=device)
        _model.load_state_dict(state_dict)
        print("Loaded model from state_dict using app/model_def/architecture.py.")

    _model.to(device)
    _model.eval()
    return _model


def predict(image: Image.Image) -> dict:
    if _model is None:
        raise RuntimeError("Model not loaded. Call load_model() at startup.")

    image = image.convert("RGB")
    tensor = _TRANSFORM(image).unsqueeze(0).to(device)

    with torch.no_grad():
        logits = _model(tensor)
        probs = F.softmax(logits, dim=1)[0].cpu().tolist()

    predicted_index = max(range(len(probs)), key=lambda i: probs[i])

    return {
        "predicted_class": config.CLASS_NAMES[predicted_index],
        "confidence": round(probs[predicted_index] * 100, 2),
        "probabilities": {
            config.CLASS_NAMES[i]: round(p * 100, 2) for i, p in enumerate(probs)
        },
    }
