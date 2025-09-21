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

def predict(model_name, img_bytes):
    """
    Predict the most confident class for a given image using the specified model.
    Returns a single dictionary with label and confidence.
    """
    if model_name not in loaded_models:
        raise ValueError(f"Model {model_name} not loaded")

    model = loaded_models[model_name]
    x = preprocess_image(img_bytes)
    preds = model.predict(x)[0]

    # Get index of most confident class
    top_idx = np.argmax(preds)
    top_label = model.class_labels[top_idx]
    top_confidence = float(preds[top_idx])

    # Return single result
    result = {"label": top_label, "confidence": top_confidence}
    return result
