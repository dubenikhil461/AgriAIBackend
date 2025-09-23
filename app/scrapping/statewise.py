# run_scraper.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import UpdateOne
from app.config.db import db
from app.scrapping.comodities import commodities, state
import pytz
from time import sleep
import random
import dotenv
import os

# ---------------- Config ----------------
URL = "https://agmarknet.gov.in/SearchCmmMkt.aspx"

HEADERS = { 
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8', 
    'accept-language': 'en-GB,en;q=0.7', 
    'priority': 'u=0, i', 
    'referer': 'https://agmarknet.gov.in/', 
    'sec-ch-ua': '"Not;A=Brand";v="99", "Brave";v="139", "Chromium";v="139"', 
    'sec-ch-ua-mobile': '?0', 
    'sec-ch-ua-platform': '"macOS"', 
    'sec-fetch-dest': 'document', 
    'sec-fetch-mode': 'navigate', 
    'sec-fetch-site': 'same-origin', 
    'sec-fetch-user': '?1', 
    'sec-gpc': '1', 
    'upgrade-insecure-requests': '1', 
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36', 
  }

IST = pytz.timezone("Asia/Kolkata")
dotenv.load_dotenv()
# Comma-separated proxies in environment variable (optional)
PROXIES = os.getenv("PROXIES", "").split(",")

# ------------- Helper Functions -------------

def get_proxy():
    if not PROXIES or PROXIES[0] == "":
        return None
    proxy_ip = random.choice(PROXIES)
    return {"http": f"http://{proxy_ip}", "https": f"http://{proxy_ip}"}

def fetch_and_store(state_item: dict, commodity_item: dict, date_str: str, max_retries=3):
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

    for attempt in range(1, max_retries + 1):
        proxy = get_proxy()
        proxy_info = proxy["http"] if proxy else "No Proxy"
        try:
            print(f"🔄 Attempt {attempt}: Fetching {commodity_item['name']} in {state_item['name']} using {proxy_info}")
            response = requests.get(URL, headers=HEADERS, params=params, proxies=proxy, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            table = soup.find("table", {"id": "cphBody_GridPriceData"})
            if not table:
                print(f"⚠️ No table found for {commodity_item['name']} in {state_item['name']}")
                return

            operations = []
            for row in table.find_all("tr")[1:]:
                cols = [td.get_text(strip=True) for td in row.find_all("td")]
                if len(cols) != 10:
                    continue
                try:
                    price_date = IST.localize(datetime.strptime(cols[9], "%d %b %Y"))
                    last_updated_ist = datetime.now(IST).replace(tzinfo=None)

                    filter_query = {
                        "state": state_item["name"],
                        "district": cols[1],
                        "market": cols[2],
                        "commodity": cols[3],
                        "variety": cols[4],
                        "grade": cols[5],
                    }

                    record = {
                        **filter_query,
                        "min_price": float(cols[6]),
                        "max_price": float(cols[7]),
                        "modal_price": float(cols[8]),
                        "price_date": price_date,
                        "LastUpdated": last_updated_ist,
                    }

                    operations.append(UpdateOne(filter_query, {"$set": record}, upsert=True))
                except Exception as parse_err:
                    print(f"⚠️ Skipping row due to parsing error: {parse_err}")
                    continue

            if operations:
                collection_name = state_item["name"].replace(" ", "_")
                collection = db[collection_name]
                result = collection.bulk_write(operations)
                print(f"✅ Processed {len(operations)} records for {commodity_item['name']} in {state_item['name']} "
                      f"- New: {result.upserted_count}, Updated: {result.modified_count}")
            else:
                print(f"⚠️ No valid rows found for {commodity_item['name']} in {state_item['name']}")
            return  # success

        except Exception as e:
            print(f"❌ Error on attempt {attempt} for {commodity_item['name']} in {state_item['name']}: {e}")
            sleep(2)

    print(f"❌ All {max_retries} attempts failed for {commodity_item['name']} in {state_item['name']}")

# ------------- Main Job -------------

def run_job():
    now = datetime.now(IST)
    current_date = now.strftime("%d-%b-%Y")

    print(f"🕒 Starting scraper at {now}")

    for s in state:
        for c in commodities:
            fetch_and_store(s, c, current_date)

    print(f"✅ Job completed at {datetime.now(IST)}")

# ------------- If running directly -------------
if __name__ == "__main__":
    run_job()
