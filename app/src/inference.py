import io
import numpy as np
from tensorflow.keras.models import load_model
from .utils import preprocess_image

loaded_models = {}

def load_model_by_name(model_name, model_path, class_names):
    model = load_model(model_path)
    model.class_names = class_names
    loaded_models[model_name] = model
    return model

def predict(model_name, img_bytes, topk=3):
    if model_name not in loaded_models:
        raise ValueError(f"Model {model_name} not loaded")
    model = loaded_models[model_name]
    x = preprocess_image(img_bytes)
    preds = model.predict(x)[0]
    top_idxs = preds.argsort()[-topk:][::-1]
    results = [{"label": list(model.class_names.keys())[i], "confidence": float(preds[i])} for i in top_idxs]
    return results
