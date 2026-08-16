import requests
import json
import os
import time

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

HEADERS = {
    "User-Agent": "GeospatialCrawlerAssignment/1.0",
    "Content-Type": "application/x-www-form-urlencoded"
}

CITIES = {
    "lagos": {
        "south": 6.39,
        "west": 3.15,
        "north": 6.70,
        "east": 3.65
    },
    "abuja": {
        "south": 8.90,
        "west": 7.30,
        "north": 9.25,
        "east": 7.60
    }
}

CATEGORIES = {
    "restaurant": "amenity=restaurant",
    "fast_food": "amenity=fast_food",
    "hotel": "tourism=hotel",
    "bakery": "shop=bakery",
    "supermarket": "shop=supermarket"
}

RAW_DATA_DIR = "data/raw"


def build_query(bbox, tag):
    key, value = tag.split("=")
    query = (
        "[out:json][timeout:60];"
        "("
        f'node["{key}"="{value}"]({bbox["south"]},{bbox["west"]},{bbox["north"]},{bbox["east"]});'
        f'way["{key}"="{value}"]({bbox["south"]},{bbox["west"]},{bbox["north"]},{bbox["east"]});'
        ");"
        "out center;"
    )
    return query


def fetch_data(city_name, bbox, category_name, tag):
    query = build_query(bbox, tag)
    print(f"Fetching {category_name} in {city_name}...")

    response = requests.post(
        OVERPASS_URL,
        data={"data": query},
        headers=HEADERS
    )

    if response.status_code != 200:
        print(f"Failed: {city_name} - {category_name} - status {response.status_code}")
        print(f"Response: {response.text[:300]}")
        return None

    return response.json()


def save_raw(data, city_name, category_name):
    if not os.path.exists(RAW_DATA_DIR):
        os.makedirs(RAW_DATA_DIR)

    filename = f"{city_name}_{category_name}.json"
    filepath = os.path.join(RAW_DATA_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Saved: {filepath}")


def run_extraction():
    for city_name, bbox in CITIES.items():
        for category_name, tag in CATEGORIES.items():
            data = fetch_data(city_name, bbox, category_name, tag)
            if data is not None:
                save_raw(data, city_name, category_name)
            time.sleep(2)


if __name__ == "__main__":
    run_extraction()