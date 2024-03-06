import requests
import hashlib
import json
from datetime import datetime
import time
import os
import notify



def fetch(url):
    """Fetch content of the URL."""

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "*/*"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text


def fetch_availability(month):
    url = month_availability(month)
    res = fetch(url)
    data = json.loads(res)
    return json.dumps(data["payload"]["availability"])

def month_availability(month):
    date = month_date(month)
    return "https://www.recreation.gov/api/permits/250014/availability/month?start_date={}T00:00:00.000Z&commercial_acct=false&is_lottery=false".format(date)

def hash(content):
    """Calculate MD5 hash of the given content."""
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def run_check_month(month):
    month_file = json_file(month)
    old_json = ""

    # Check if the hash file exists to compare with the previous hash
    if os.path.exists(month_file):
        with open(month_file, 'r') as file:
            old_json = file.read()

    new_json = fetch_availability(month)
    old_hash = hash(old_json)
    new_hash = hash(new_json)

    if (old_hash != new_hash):
        print("DIFF", month, "old={}".format(old_hash), "new={}".format(new_hash))
        notify_user(month)

        # record results in HASH.json
        with open(json_file(new_hash), 'w') as file:
            file.write(new_json)

        # record results in MON.json
        with open(month_file, 'w') as file:
            file.write(new_json)


def run_check():
    now = datetime.now()
    print("RUN", now)
    for month in months():
        run_check_month(month)

def months():
    return ["may", "jun", "jul", "aug", "sep"]


def month_date(m):
    if m == "may":
        return "2024-05-01"
    elif m == "jun":
        return "2024-06-01"
    elif m == "jul":
        return "2024-07-01"
    elif m == "aug":
        return "2024-08-01"
    elif m == "sep":
        return "2024-09-01"

def json_file(m):
    return "data/{}.json".format(m)


def notify_user(month):
    url = "https://www.recreation.gov/permits/250014/registration/detailed-availability?date={}".format(month_date(month))
    notify.notify_user_via_email(month, url)

def main():
    print("Starting River API Scraper")

    while True:
        run_check()
        time.sleep(5*60) # in seconds

if __name__ == "__main__":
    main()
