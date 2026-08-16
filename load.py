import json
import os
import pandas as pd

RAW_DATA_DIR = "data/raw"
PROCESSED_DATA_DIR = "data/processed"
OUTPUT_FILE = "loaded_raw.csv"


def parse_element(element, city_name, category_name):
    tags = element.get("tags", {})
    name = tags.get("name")

    if element["type"] == "node":
        lat = element.get("lat")
        lon = element.get("lon")
    else:
        center = element.get("center", {})
        lat = center.get("lat")
        lon = center.get("lon")

    address_parts = [
        tags.get("addr:housenumber", ""),
        tags.get("addr:street", ""),
        tags.get("addr:city", "")
    ]
    address = " ".join(part for part in address_parts if part).strip()

    return {
        "name": name,
        "category": category_name,
        "city": city_name,
        "latitude": lat,
        "longitude": lon,
        "address": address if address else None
    }


def load_raw_files():
    rows = []

    if not os.path.exists(RAW_DATA_DIR):
        print(f"No raw data directory found at {RAW_DATA_DIR}")
        return rows

    for filename in os.listdir(RAW_DATA_DIR):
        if not filename.endswith(".json"):
            continue

        parts = filename.replace(".json", "").split("_", 1)
        if len(parts) != 2:
            continue

        city_name, category_name = parts
        filepath = os.path.join(RAW_DATA_DIR, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        elements = data.get("elements", [])
        for element in elements:
            row = parse_element(element, city_name, category_name)
            rows.append(row)

    return rows


def run_load():
    rows = load_raw_files()
    df = pd.DataFrame(rows)

    if not os.path.exists(PROCESSED_DATA_DIR):
        os.makedirs(PROCESSED_DATA_DIR)

    output_path = os.path.join(PROCESSED_DATA_DIR, OUTPUT_FILE)
    df.to_csv(output_path, index=False)

    print(f"Loaded {len(df)} rows into {output_path}")
    return df


if __name__ == "__main__":
    run_load()