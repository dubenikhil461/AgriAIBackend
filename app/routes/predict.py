from fastapi import APIRouter, UploadFile, File
from tensorflow.keras.models import load_model
import numpy as np
from PIL import Image

# Router
router = APIRouter()

# Load model
model = load_model("app/models/disease_model.h5")

# Load class names
with open("app/models/class_names.txt") as f:
    class_names = [line.strip() for line in f]

@router.post("/predict")
async def predict(file: UploadFile = File(...)):
    # Read file
    img = Image.open(file.file).convert("RGB")
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)  # (1,224,224,3)

    # Prediction
    preds = model.predict(img_array)
    idx = np.argmax(preds[0])
    result = {
        "class": class_names[idx],
        "confidence": float(np.max(preds[0]))
    }
    return result
