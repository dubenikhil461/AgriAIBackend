from fastapi import APIRouter, HTTPException, Query
from app.config.db import db
from datetime import datetime
from typing import  Dict, Any, List

router = APIRouter()

# ---------- Helpers ----------
def get_collection(state: str):
    """Return MongoDB collection for a state"""
    try:
        return db[state.replace(" ", "_")]
    except Exception:
        raise HTTPException(status_code=400, detail=f"Invalid state: {state}")

def format_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Convert MongoDB document into JSON-serializable dict"""
    doc["_id"] = str(doc.get("_id"))
    if "price_date" in doc and isinstance(doc["price_date"], datetime):
        doc["price_date"] = doc["price_date"].isoformat()
    return doc

def distinct_nonempty(collection, field: str, query: Dict = {}) -> List[str]:
    """Get non-empty distinct values for a field"""
    values = collection.distinct(field, query)
    return sorted([v for v in values if v and str(v).strip()])

# ---------- Routes ----------

@router.get("/states")
def get_states():
    """Return all available states"""
    states = ["Kerala", "Maharashtra", "Uttar Pradesh", "NCT_of_Delhi"]
    return {"states": states, "count": len(states)}

@router.get("/district")
def get_districts(state: str):
    collection = get_collection(state)
    districts = distinct_nonempty(collection, "district")
    return {"districts": districts, "count": len(districts), "state": state}

@router.get("/markets")
def get_markets(state: str, district: str):
    collection = get_collection(state)
    markets = distinct_nonempty(collection, "market", {"district": district})
    return {"markets": markets, "count": len(markets), "state": state, "district": district}

@router.get("/data")
def get_data(state: str, district: str, market: str,commodity: str,limit: int = 100):
    """
    After selecting state -> district -> market,
    return all documents for that selection with all keys
    """
    collection = get_collection(state)
    cursor = collection.find({"district": district, "market": market,"commodity":commodity}).limit(limit)
    results = [format_doc(doc) for doc in cursor]
    return {
        "data": results,
        "count": len(results),
        "state": state,
        "district": district,
        "market": market,
        "last_updated": datetime.now().isoformat()
    }
