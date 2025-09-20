from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from src.inference import load_model_by_name, predict
from src.train_model import train_model

import os

app = FastAPI(title="SIH Multi-Model API")

# ---------------- Load all models at startup ----------------
models_to_load = {
    "model1": {
        "path": "app/models/model1/best_model.h5",
        "class_names": {}  # populate from train_model output
    },
    "model2": {
        "path": "app/models/model2/best_model.h5",
        "class_names": {}
    }
}

for name, info in models_to_load.items():
    if os.path.exists(info["path"]):
        load_model_by_name(name, info["path"], info["class_names"])
        print(f"Loaded {name}")

# ---------------- Predict endpoint ----------------
@app.post("/predict/{model_name}")
async def predict_endpoint(model_name: str, file: UploadFile = File(...)):
    try:
        img_bytes = await file.read()
        results = predict(model_name, img_bytes, topk=3)
        return JSONResponse({"predictions": results})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
