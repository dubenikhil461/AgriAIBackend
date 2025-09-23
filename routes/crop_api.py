from fastapi import APIRouter
from pydantic import BaseModel
import joblib
import numpy as np

router = APIRouter()

# Load trained model
crop_model = joblib.load("models/crop_model.pkl")

class CropInput(BaseModel):
    N: int
    P: int
    K: int
    temperature: float
    humidity: float
    ph: float
    rainfall: float

@router.post("/recommend-crop")
def recommend_crop(data: CropInput):
    features = np.array([[data.N, data.P, data.K, data.temperature, data.humidity, data.ph, data.rainfall]])
    prediction = crop_model.predict(features)[0]
    return {"recommended_crop": prediction}
