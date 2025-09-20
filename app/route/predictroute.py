from fastapi import File, UploadFile,APIRouter
from fastapi.responses import JSONResponse
from app.src import inference
import os

router = APIRouter()

# ---------------- Load all models ----------------
models_to_load = {
    "model1": {
        "path": "app/models/model1/best_model.h5",
    },
    "model2": {
        "path": "app/models/model2/best_model.h5",
    }
}

for name, info in models_to_load.items():
    model_path = info["path"]
    class_indices_path = model_path.replace('best_model.h5', 'class_indices.txt')
    if os.path.exists(model_path) and os.path.exists(class_indices_path):
        inference.load_model_by_name(name, model_path, class_indices_path)


# ---------------- Predict endpoint ----------------
@router.post("/predict/{model_name}")
async def predict_endpoint(model_name: str, file: UploadFile = File(...)):
    try:
        img_bytes = await file.read()
        result = inference.predict(model_name, img_bytes)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
