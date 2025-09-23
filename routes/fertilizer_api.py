from fastapi import APIRouter
from pydantic import BaseModel
import joblib
import numpy as np

router = APIRouter()

# Load trained fertilizer model
fertilizer_model = joblib.load("models/fertilizer_model.pkl")

# Request schema
class FertilizerInput(BaseModel):
    Nitrogen: int
    Phosphorous: int
    Potassium: int
    Temparature: float
    Humidity: float

@router.post("/recommend-fertilizer")
def recommend_fertilizer(data: FertilizerInput):
    features = np.array([[data.Nitrogen, data.Phosphorous, data.Potassium,
                          data.Temparature, data.Humidity]])
    prediction = fertilizer_model.predict(features)[0]
    return {"recommended_fertilizer": prediction}
