import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import UpdateOne
from app.config.db import db
from app.scrapping.comodities import commodities, state
import pytz
from time import sleep
import random

URL = "https://agmarknet.gov.in/SearchCmmMkt.aspx"

HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8', 
    'accept-language': 'en-GB,en;q=0.5', 
    'cache-control': 'no-cache', 
    'pragma': 'no-cache', 
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

# ----- Add all proxies here -----
PROXIES_LIST = [
    "8.219.97.248:80","47.251.43.115:33333","213.35.105.30:8080","147.75.34.105:443",
    "147.75.33.104:10094","57.129.81.201:999","52.67.251.34:80","194.145.200.184:3128",
    "211.230.49.122:3128","179.96.28.58:80","52.148.130.219:8080","200.174.198.158:8888",
    "66.36.234.130:1339","222.252.194.29:8080","138.197.68.35:4857","188.166.197.129:3128",
    "195.158.8.123:3128","102.222.161.143:3128","188.166.230.109:31028","185.226.118.159:10808",
    "14.225.240.23:8562","157.180.121.252:21829","72.10.160.94:28161","107.174.54.213:3128",
    "185.112.151.207:8022","103.155.196.105:8080","85.132.37.9:1313","193.124.183.19:1080",
    "8.211.195.173:992","129.159.114.120:8080","8.243.68.10:8080","35.193.78.97:8080",
    "157.66.51.155:8080","34.170.24.59:3128","190.242.157.215:8080","112.216.83.10:3128",
    "202.59.89.43:8080","23.237.210.82:80","35.154.84.167:80","8.209.255.13:3128",
    "8.213.151.128:3128","209.14.98.6:8080","8.212.165.33:3333","41.223.119.156:3128",
    "47.89.184.18:3128","47.91.65.23:3128","35.226.66.119:8080","91.84.99.28:80",
    "48.218.198.55:8080","93.113.63.73:33100","217.138.18.72:8080","200.85.167.254:8080",
    "176.9.164.117:60009","166.249.54.61:7234","20.78.26.206:8561","221.202.27.194:10811",
    "157.230.220.25:4857","115.72.11.160:10004","38.225.225.20:8080","194.53.194.51:8080",
    "128.140.113.110:3128","145.223.74.203:8080","104.238.30.17:54112","95.47.239.65:3128",
    "23.236.65.234:38080","67.43.228.252:28007","103.147.250.93:1452","167.172.162.147:3128",
    "23.95.248.47:5566","147.93.43.7:8080","72.10.160.90:1237","109.135.16.145:8789",
    "94.182.146.250:8080","80.78.75.80:8080","202.5.47.44:5555","101.255.211.54:8082",
    "115.187.30.171:1111","124.83.51.80:8082","103.210.22.17:3128","201.190.178.205:8080",
    "64.181.240.152:3128","118.70.13.38:41857","164.90.151.28:3128","222.59.173.105:45053",
    "140.238.184.182:3128","135.181.213.184:40028","116.101.225.47:12008","180.105.65.66:1080",
    "20.27.11.248:8561","167.88.43.46:8080","36.147.78.166:80","144.124.228.87:1080",
    "173.249.37.45:5005","217.77.102.18:3128","118.27.111.97:80","187.217.194.178:8080",
    "78.188.75.172:8080","139.162.13.186:8888","38.194.231.70:999","223.26.61.69:8080"
]

def get_working_proxy():
    """Return a random working proxy from the list."""
    proxy_ip = random.choice(PROXIES_LIST)
    proxies = {
        "http": f"http://{proxy_ip}",
        "https": f"http://{proxy_ip}"
    }
    return proxies

def fetch_and_store(state_item: dict, commodity_item: dict, date_str: str):
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

    attempt = 0
    max_attempts = len(PROXIES_LIST)
    while attempt < max_attempts:
        proxies = get_working_proxy()
        try:
            print(f"🔄 Fetching {commodity_item['name']} in {state_item['name']} using proxy {proxies['http']}")
            response = requests.get(URL, headers=HEADERS, params=params, proxies=proxies, timeout=15)
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
                print(f"✅ Processed {len(operations)} records for {commodity_item['name']} in {state_item['name']} - New: {result.upserted_count}, Updated: {result.modified_count}")
            else:
                print(f"⚠️ No valid rows found for {commodity_item['name']} in {state_item['name']}")

            return  # success, exit loop
        except Exception as e:
            print(f"❌ Error with proxy {proxies['http']}: {e}, trying next proxy...")
            attempt += 1
            sleep(1)
    print(f"❌ All proxies failed for {commodity_item['name']} in {state_item['name']}")

def run_job():
    now = datetime.now(IST)
    current_date = now.strftime("%d-%b-%Y")

    for s in state:
        for c in commodities:
            fetch_and_store(s, c, current_date)

    print(f"Job completed at {now}")
