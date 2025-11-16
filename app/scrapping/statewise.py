import requests
import time
from app.config.db import db

# Your commodity list
commodities = [
    {"value": 49, "name": "Arhar (Tur/Red Gram)(Whole)"},
    {"value": 28, "name": "Bajra(Pearl Millet/Cumbu)"},
    {"value": 29, "name": "Barley (Jau)"},
    {"value": 6, "name": "Bengal Gram(Gram)(Whole)"},
    {"value": 8, "name": "Black Gram (Urd Beans)(Whole)"},
    {"value": 129, "name": "Copra"},
    {"value": 15, "name": "Cotton"},
    {"value": 9, "name": "Green Gram (Moong)(Whole)"},
    {"value": 10, "name": "Groundnut"},
    {"value": 5, "name": "Jowar(Sorghum)"},
    {"value": 16, "name": "Jute"},
    {"value": 63, "name": "Lentil (Masur)(Whole)"},
    {"value": 4, "name": "Maize"},
    {"value": 12, "name": "Mustard"},
    {"value": 98, "name": "Niger Seed (Ramtil)"},
    {"value": 23, "name": "Onion"},
    {"value": 2, "name": "Paddy(Dhan)(Common)"},
    {"value": 24, "name": "Potato"},
    {"value": 30, "name": "Ragi (Finger Millet)"},
    {"value": 59, "name": "Safflower"},
    {"value": 11, "name": "Sesamum(Sesame,Gingelly,Til)"},
    {"value": 13, "name": "Soyabean"},
    {"value": 150, "name": "Sugarcane"},
    {"value": 14, "name": "Sunflower"},
    {"value": 285, "name": "Sunflower Seed"},
    {"value": 78, "name": "Tomato"},
    {"value": 66, "name": "Toria"},
    {"value": 1, "name": "Wheat"},
]

BASE_URL = "https://api.agmarknet.gov.in/v1/dashboard-data/"


def fetch_data(commodity_id):
    params = {
        "dashboard": "marketwise_price_arrival",
        "date": "2025-11-16",
        "group": "[100000]",
        "commodity": f"[{commodity_id}]",
        "variety": "100021",
        "state": 17,  # Kerala
        "district": "[100007,270,271,272,273,274,275,276,277,278,279,280,281,282,283,284,285]",
        "grades": "[4]",
        "limit": 30,
        "format": "json",
    }

    headers = {
        "accept": "application/json, text/plain, */*",
        "origin": "https://agmarknet.gov.in",
        "referer": "https://agmarknet.gov.in/",
        "user-agent": "Mozilla/5.0",
    }

    try:
        r = requests.get(BASE_URL, params=params, headers=headers, timeout=20)
        return r.json()
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def save_to_db(commodity_name, commodity_id, api_response):
    """Handles both list and dict API responses safely."""
    collection = db["statewise_prices"]

    # Case 1: API returned list → unexpected → store empty but valid
    if isinstance(api_response, list):
        print(f"⚠️ WARNING: API returned list for {commodity_name}, saving empty.")
        doc = {
            "commodity_id": commodity_id,
            "commodity_name": commodity_name,
            "state": "Kerala",
            "records": [],
        }
        collection.insert_one(doc)
        return

    # Case 2: API returned dict → correct format
    if isinstance(api_response, dict):
        data_section = api_response.get("data", {})

        # If "data" itself is list — avoid crash
        if isinstance(data_section, list):
            print(f"⚠️ WARNING: 'data' is list for {commodity_name}, saving empty.")
            doc = {
                "commodity_id": commodity_id,
                "commodity_name": commodity_name,
                "state": "Kerala",
                "records": [],
            }
            collection.insert_one(doc)
            return

        records = data_section.get("records", [])

        doc = {
            "commodity_id": commodity_id,
            "commodity_name": commodity_name,
            "state": "Kerala",
            "records": records,
        }

        collection.insert_one(doc)
        print(f"✅ Saved → {commodity_name} (ID: {commodity_id})")
        return

    # Case 3: Unexpected data type
    print(f"❌ ERROR: Unknown API response type for {commodity_name}. Saving empty.")
    doc = {
        "commodity_id": commodity_id,
        "commodity_name": commodity_name,
        "state": "Kerala",
        "records": [],
    }
    collection.insert_one(doc)


def run_scraper():
    for item in commodities:
        print("\n========================================================")
        print(f"Fetching → {item['name']}")
        print("========================================================")

        response = fetch_data(item["value"])
        save_to_db(item["name"], item["value"], response)

        time.sleep(1)  # Avoid rate-limit


if __name__ == "__main__":
    run_scraper()
