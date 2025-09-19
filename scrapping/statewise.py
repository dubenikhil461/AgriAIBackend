import requests
from bs4 import BeautifulSoup
from comodities import commodities, state
from datetime import datetime, timedelta
from pymongo import MongoClient, UpdateOne
import pytz
from apscheduler.schedulers.blocking import BlockingScheduler
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Access variables
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")



URL = "https://agmarknet.gov.in/SearchCmmMkt.aspx"
HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "accept-language": "en-GB,en;q=0.7",
    "referer": "https://agmarknet.gov.in/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
}


# Timezone
IST = pytz.timezone("Asia/Kolkata")


# -------------------- RULE CHECK --------------------
def should_fetch_today() -> bool:
    """
    Rules:
    - Daily updates until 11:30 PM
    - Friday & Saturday updates allowed only till Monday 11:30 PM
    - Only allow scraping between 6 AM and 6 PM
    """
    now = datetime.now(IST)

    # Time window: 6 AM - 6 PM only
    if not (6 <= now.hour < 18):
        return False

    # Check if today is Friday or Saturday
    if now.weekday() in [4, 5]:  # Fri=4, Sat=5
        # Allowed till Monday 11:30 PM
        monday_deadline = (now + timedelta(days=(7 - now.weekday()))).replace(
            hour=23, minute=30, second=0, microsecond=0
        )
        return now <= monday_deadline

    # For other days, allow until 11:30 PM
    today_deadline = now.replace(hour=23, minute=30, second=0, microsecond=0)
    return now <= today_deadline


# -------------------- FETCH & STORE --------------------
def fetch_and_store(state_item, commodity_item, date_str, db):
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
        print(f"Fetching data for {commodity_item['name']} in {state_item['name']}...")
        response = requests.get(URL, headers=HEADERS, params=params, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find("table", {"id": "cphBody_GridPriceData"})

        if not table:
            print(f"❌ No data table found for {commodity_item['name']} in {state_item['name']}")
            return

        rows = table.find_all("tr")
        data_list = []

        for row in rows[1:]:
            cols = [td.get_text(strip=True) for td in row.find_all("td")]
            if cols and len(cols) == 10:
                try:
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
                        "price_date": datetime.strptime(cols[9], "%d %b %Y"),
                    }
                    data_list.append(record)
                except Exception as parse_err:
                    print(f"⚠️ Skipping row due to parse error: {parse_err}")

        if data_list:
            # 🔥 Dynamic collection name (one collection per state)
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
                print(
                    f"✅ {collection_name}: {result.upserted_count} new, {result.modified_count} updated."
                )
        else:
            print(f"⚠️ No rows found for {commodity_item['name']} in {state_item['name']}")

    except Exception as e:
        print(f"❌ Error: {e}")


# -------------------- MAIN JOB --------------------
def run_job():
    now = datetime.now(IST)
    current_date = now.strftime("%d-%b-%Y")

    if not should_fetch_today():
        print(f"⏭ Skipping fetch at {now} (rules/time not allowed)")
        return

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    for s in state:
        for c in commodities:
            fetch_and_store(s, c, current_date, db)

    print(f"\n✅ Job completed at {now}\n")


# -------------------- SCHEDULER --------------------
def main():
    run_job()
    scheduler = BlockingScheduler(timezone=IST)
    # Run every 3 hours between 6 AM - 6 PM
    scheduler.add_job(run_job, "cron", hour="6,9,12,15,18")
    print("🚀 Scheduler started... Fetching every 3 hours (6 AM - 6 PM IST).")
    scheduler.start()


if __name__ == "__main__":
    main()
