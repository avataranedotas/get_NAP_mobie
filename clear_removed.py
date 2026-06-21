#!/usr/bin/env python3

import json
import sys
from pathlib import Path


def filter_evses(original_path: str, status_path: str, output_path: str) -> None:
    with open(original_path, "r", encoding="utf-8") as f:
        original = json.load(f)

    with open(status_path, "r", encoding="utf-8") as f:
        status = json.load(f)

    # Build a lookup: station_key -> evse_code -> status
    # Status file uses evse_id which matches evse_code in the original file
    status_lookup: dict[str, dict[str, str]] = {}
    for station_key, station_data in status.items():
        evse_statuses = {}
        for station in station_data.get("stations", []):
            for evse in station.get("evses", []):
                evse_id = evse.get("evse_id", "")
                evse_status = evse.get("evse_status", "")
                evse_statuses[evse_id] = evse_status
        status_lookup[station_key] = evse_statuses

    filtered = {}
    stats = {"stations_kept": 0, "stations_dropped": 0, "evses_kept": 0, "evses_removed": 0}

    for station_key, station_data in original.items():
        evse_statuses = status_lookup.get(station_key, {})

        # Deep copy station data and filter evses inside each station
        new_station_data = {k: v for k, v in station_data.items() if k != "stations"}
        new_stations = []

        for station in station_data.get("stations", []):
            new_evses = []
            for evse in station.get("evses", []):
                evse_code = evse.get("evse_code", "")
                evse_status = evse_statuses.get(evse_code, None)

                if evse_status == "removed":
                    stats["evses_removed"] += 1
                else:
                    # Keep if status is not "removed" (including unknown/missing status)
                    new_evses.append(evse)
                    stats["evses_kept"] += 1

            if new_evses:
                new_station = {k: v for k, v in station.items() if k != "evses"}
                new_station["evses"] = new_evses
                new_stations.append(new_station)

        if new_stations:
            new_station_data["stations"] = new_stations
            filtered[station_key] = new_station_data
            stats["stations_kept"] += 1
        else:
            # All EVSEs were removed — drop the entire station entry
            stats["stations_dropped"] += 1

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(filtered, f, indent=4, ensure_ascii=False)

    print(f"Done! Results written to: {output_path}")
    print(f"  Stations kept:    {stats['stations_kept']}")
    print(f"  Stations dropped: {stats['stations_dropped']} (all EVSEs were removed)")
    print(f"  EVSEs kept:       {stats['evses_kept']}")
    print(f"  EVSEs removed:    {stats['evses_removed']}")


if __name__ == "__main__":
    
    original_path = "LATEST_static.json"
    status_path = "LATEST_dynamic.json"
    output_path = "LATEST_static_filtered.json"

    filter_evses(original_path, status_path, output_path)
