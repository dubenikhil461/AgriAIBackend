from fastapi import APIRouter
from app.config.db import db

router = APIRouter()


@router.get("/statewise-prices")
def get_statewise_prices():
    """Get all statewise price data from database."""
    collection = db["statewise_prices"]
    
    # Synchronous MongoDB query
    documents = list(collection.find({}))
    
    # Convert ObjectId to string
    for doc in documents:
        doc["_id"] = str(doc["_id"])
    
    return {"status": "success", "data": documents}