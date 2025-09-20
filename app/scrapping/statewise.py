import requests
from bs4 import BeautifulSoup
from app.scrapping.comodities import commodities, state
from datetime import datetime
from pymongo import UpdateOne
from app.config.db import db  # your MongoDB connection
import pytz

# -------------------- CONFIG --------------------
URL = "https://agmarknet.gov.in/SearchCmmMkt.aspx"
HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "accept-language": "en-GB,en;q=0.7",
    "referer": "https://agmarknet.gov.in/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
}

IST = pytz.timezone("Asia/Kolkata")

# -------------------- FETCH & STORE --------------------
def fetch_and_store(state_item: dict, commodity_item: dict, date_str: str, db):
    """
    Fetch commodity prices for a given state and store in MongoDB.
    """
    params = {
        "Tx_Commodity": str(commodity_item["value"]),
        "Tx_State": state_item["value"],
        "Tx_District": "0",
        "Tx_Market": "0",
        "DateFrom": date_str,
        "DateTo": date_str,
        "Tx_Trend": "0",
        "Tx_CommodityHead": commodity_item["name"],
        "Tx_StateHead": state_item["name"],
    }

    try:
        print(f"Fetching {commodity_item['name']} prices in {state_item['name']}...")
        response = requests.get(URL, headers=HEADERS, params=params, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find("table", {"id": "cphBody_GridPriceData"})

        if not table:
            print(f"❌ No data found for {commodity_item['name']} in {state_item['name']}")
            return

        rows = table.find_all("tr")
        data_list = []

        for row in rows[1:]:
            cols = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cols) != 10:
                continue  # skip invalid rows

            try:
                price_date = datetime.strptime(cols[9], "%d %b %Y")
                price_Date = IST.localize(price_date)
                record = {
                    "state": state_item["name"],
                    "district": cols[1],
                    "market": cols[2],
                    "commodity": cols[3],
                    "variety": cols[4],
                    "grade": cols[5],
                    "min_price": float(cols[6]),
                    "max_price": float(cols[7]),
                    "modal_price": float(cols[8]),
                    "price_date": price_Date,
                    "LastUpdated": datetime.strptime("%d-%b-%Y %H:%M:%S"),
                }
                data_list.append(record)
            except Exception as parse_err:
                print(f"⚠️ Skipping row due to parse error: {parse_err}")

        if data_list:
            collection_name = state_item["name"].replace(" ", "_")
            collection = db[collection_name]

            operations = [
                UpdateOne(
                    {
                        "district": d["district"],
                        "market": d["market"],
                        "commodity": d["commodity"],
                        "variety": d["variety"],
                        "price_date": d["price_date"],
                    },
                    {"$set": d},
                    upsert=True,
                )
                for d in data_list
            ]

            if operations:
                result = collection.bulk_write(operations)
                print(f"✅ {collection_name}: {result.upserted_count} new, {result.modified_count} updated.")
        else:
            print(f"⚠️ No rows found for {commodity_item['name']} in {state_item['name']}")

    except requests.RequestException as req_err:
        print(f"❌ HTTP Error: {req_err}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


# -------------------- MAIN JOB --------------------
def run_job():
    """
    Run scraper for all states and commodities for today's date.
    """
    now = datetime.now(IST)
    current_date = now.strftime("%d-%b-%Y")

    for s in state:
        for c in commodities:
            fetch_and_store(s, c, current_date, db)

    print(f"\n✅ Job completed at {now}\n")
