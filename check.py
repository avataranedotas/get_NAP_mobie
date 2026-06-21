#!/usr/bin/env python3
"""
check_evse_codes.py - Check if all evse_codes in the filtered JSON exist in a reference text file.

Usage:
    python check_evse_codes.py <filtered.json> <evse_codes.txt>

Prints only evse_codes that are in the JSON but NOT in the text file.
"""

import json
import sys
from pathlib import Path


def check_evse_codes(json_path: str, txt_path: str) -> None:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(txt_path, "r", encoding="utf-8") as f:
        reference_codes = {line.strip() for line in f if line.strip()}

    missing = []

    for station_key, station_data in data.items():
        for station in station_data.get("stations", []):
            for evse in station.get("evses", []):
                evse_code = evse.get("evse_id", "").strip()
                if evse_code and evse_code not in reference_codes:
                    missing.append((station_key, evse_code))

    if missing:
        print(f"Found {len(missing)} evse_code(s) NOT in the reference file:\n")
        for station_key, evse_code in missing:
            print(f"  [{station_key}]  {evse_code}")
    else:
        print("All evse_codes in the filtered file are present in the reference file.")


if __name__ == "__main__":
   

    check_evse_codes("LATEST_static_filtered.json", "lista_evses_osm.txt")
