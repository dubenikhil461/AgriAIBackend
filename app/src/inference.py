import io
import numpy as np
from tensorflow.keras.models import load_model
from .utils import preprocess_image

loaded_models = {}

def load_model_by_name(model_name, model_path, class_indices_path):
    """
    Load a model from disk and attach class labels from a .txt file.
    """
    model = load_model(model_path)
    
    # Load class indices from txt
    class_names = {}
    with open(class_indices_path, 'r') as f:
        for line in f:
            if ':' in line:
                cls, idx = line.strip().split(':')
                class_names[cls.strip()] = int(idx.strip())
    
    # Convert to list for easy indexing
    labels = [None] * len(class_names)
    for label, idx in class_names.items():
        labels[idx] = label
    model.class_labels = labels
    
    loaded_models[model_name] = model
    print(f"Loaded model: {model_name}")
    return model

def predict(model_name, img_bytes, topk=1):
    """
    Predict top-k classes for a given image using the specified model.
    Default topk=1 for only the most confident prediction.
    """
    if model_name not in loaded_models:
        raise ValueError(f"Model {model_name} not loaded")

    model = loaded_models[model_name]
    x = preprocess_image(img_bytes)
    preds = model.predict(x)[0]

    # Get top-k indices
    top_idxs = preds.argsort()[-topk:][::-1]
    
    # Build results
    results = [{"label": model.class_labels[i], "confidence": float(preds[i])} for i in top_idxs]
    return results
