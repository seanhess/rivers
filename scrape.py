import requests
import hashlib
import json
from datetime import datetime
import time
# from typing import Dict, TypedDict
import os
import notify
import random

# class Availability(TypedDict):
#     total: int
#     remaining: int
#
# class DivisionAvailability(TypedDict):
#     division_id: str
#     date_availability: Dict[str, Availability]


def fetch(url):
    """Fetch content of the URL."""

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "*/*"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text


def fetch_availability(permit, month): # -> Dict[str, DivisionAvailability]:
    url = month_availability(permit, month)
    res = fetch(url)
    data = json.loads(res)
    return data["payload"]["availability"]

def month_availability(permit, month):
    date = month_date(month)
    return "https://www.recreation.gov/api/permits/{}/availability/month?start_date={}T00:00:00.000Z&commercial_acct=false&is_lottery=false".format(permit, date)

def hash(content:str) -> str:
    """Calculate MD5 hash of the given content."""
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def run_check_month(permit, month):
    month_file = json_file("{}-{}".format(permit, month))
    old_json_str = ""

    # Check if the hash file exists to compare with the previous hash
    if os.path.exists(month_file):
        with open(month_file, 'r') as file:
            old_json_str = file.read()

    new_json = fetch_availability(permit, month)
    new_json_str = json.dumps(new_json)


    old_hash = hash(old_json_str)
    new_hash = hash(new_json_str)

    invalid = check_invalid(new_json)

    if invalid:
        print("Invalid Response: {} {}".format(month, invalid))
        return

    if (old_hash != new_hash):
        print("DIFF","permit={}".format(permit), month, "old={}".format(old_hash), "new={}".format(new_hash))
        notify_user(permit, month)

        # record results in HASH.json
        with open(json_file(new_hash), 'w') as file:
            file.write(new_json_str)

        # record results in MON.json
        with open(month_file, 'w') as file:
            file.write(new_json_str)


def check_invalid(json): # :Dict[str, DivisionAvailability]):
    for division_id in json:
        division = json[division_id]
        dates = division["date_availability"]
        if (len(dates) == 0):
            return "Missing Dates: {}".format(division_id)

    return False

def run_check():
    now = datetime.now()
    print("RUN", now)
    for permit in permits():
        for month in months():
            run_check_month(permit, month)

def months():
    return ["may", "jun", "jul", "aug", "sep", "oct"]

def permits():
    return ["250014", "233393"]


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
    elif m == "oct":
        return "2024-10-01"

def json_file(m):
    return "data/{}.json".format(m)


def notify_user(permit, month):
    url = "https://www.recreation.gov/permits/{}/registration/detailed-availability?date={}".format(permit, month_date(month))
    notify.notify_user_via_email(month, url)

def main():
    print("Starting River API Scraper")

    while True:
        run_check()
        random_seconds = random.randint(60, 5*60)
        time.sleep(random_seconds) # in seconds

if __name__ == "__main__":
    main()
