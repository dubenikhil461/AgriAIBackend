from fastapi import APIRouter, UploadFile, File, HTTPException
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os

router = APIRouter()

# Load model & classes
MODEL_PATH = os.path.join("app", "models", "disease_model.h5")
CLASS_PATH = os.path.join("app", "models", "class_names.txt")

model = tf.keras.models.load_model(MODEL_PATH)
with open(CLASS_PATH, "r") as f:
    class_names = [line.strip() for line in f.readlines()]

@router.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(status_code=400, detail="Invalid image file type")
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        image = image.resize((224, 224))
        img_array = np.array(image) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        predictions = model.predict(img_array)
        predicted_index = int(np.argmax(predictions))
        predicted_class = class_names[predicted_index]
        confidence = float(np.max(predictions))

        return {"class": predicted_class, "confidence": confidence}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {e}")
