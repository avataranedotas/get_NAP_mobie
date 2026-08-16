#!/usr/bin/env python3

import csv
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta

INPUT_FILE = "charging_evses_dyna.json"
INTERVAL_MINUTES = 5
INTERVAL_TOLERANCE_SECONDS = 60

EXPECTED_INTERVAL = timedelta(minutes=INTERVAL_MINUTES)
INTERVAL_TOLERANCE = timedelta(seconds=INTERVAL_TOLERANCE_SECONDS)


def parse_timestamp(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def load_json():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def append_raw_observations(data):
    if not data:
        return None

    timestamp = data[0]["lastUpdated"]
    dt = parse_timestamp(timestamp)

    raw_file = f"charging_{dt.strftime('%Y-%m-%d')}.csv"

    existing_keys = set()

    if Path(raw_file).exists():
        with open(raw_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                existing_keys.add(
                    (row["timestamp"], row["evse_id"])
                )

    new_rows = []

    for item in data:

        key = (
            item["lastUpdated"],
            item["evse_id"]
        )

        if key not in existing_keys:
            new_rows.append([
                item["lastUpdated"],
                item["station_id"],
                item["evse_id"]
            ])

    if new_rows:

        file_exists = Path(raw_file).exists()

        with open(
            raw_file,
            "a",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.writer(f)

            if not file_exists:
                writer.writerow([
                    "timestamp",
                    "station_id",
                    "evse_id"
                ])

            writer.writerows(new_rows)

    return raw_file


def build_summary(raw_file):

    observations = defaultdict(list)
    station_lookup = {}

    with open(raw_file, newline="", encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for row in reader:

            evse = row["evse_id"]

            observations[evse].append(
                parse_timestamp(row["timestamp"])
            )

            station_lookup[evse] = row["station_id"]

    summary_rows = []

    for evse, times in observations.items():

        times.sort()

        charging_minutes = 0
        sessions = 0

        if not times:
            continue

        # The first observation starts a session.
        sessions = 1


        for i in range(len(times) - 1):

            delta = times[i + 1] - times[i]

            if abs(delta - EXPECTED_INTERVAL) <= INTERVAL_TOLERANCE:

                # Consecutive observations confirm
                # another 5 minutes of charging.
                charging_minutes += INTERVAL_MINUTES

            else:

                # Missing observation / significant time gap.
                sessions += 1

        summary_rows.append({
            "station_id": station_lookup[evse],
            "evse_id": evse,
            "observations": len(times),
            "charging_minutes": charging_minutes,
            "sessions": sessions
        })

    summary_rows.sort(
        key=lambda r: (
	        -r["charging_minutes"],
	        -r["sessions"]
        )
    )

    summary_file = raw_file.replace(
        "charging_",
        "charging_summary_"
    )

    with open(
        summary_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "station_id",
                "evse_id",
                "observations",
                "charging_minutes",
                "sessions"
            ]
        )

        writer.writeheader()
        writer.writerows(summary_rows)

    return summary_file


def build_station_summary(evse_summary_file):

    station_data = defaultdict(
        lambda: {
            "plugs_used": 0,
            "observations": 0,
            "charging_minutes": 0,
            "sessions": 0
        }
    )

    with open(
        evse_summary_file,
        newline="",
        encoding="utf-8"
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            station = row["station_id"]

            station_data[station]["plugs_used"] += 1

            station_data[station]["observations"] += int(
                row["observations"]
            )

            station_data[station]["charging_minutes"] += int(
                row["charging_minutes"]
            )

            station_data[station]["sessions"] += int(
                row["sessions"]
            )

    station_rows = []

    for station, values in station_data.items():

        station_rows.append({
            "station_id": station,
            "plugs_used": values["plugs_used"],
            "observations": values["observations"],
            "charging_minutes": values["charging_minutes"],
            "sessions": values["sessions"]
        })

    station_rows.sort(
        key=lambda r: (
            -r["charging_minutes"],
            -r["sessions"]
        )
    )

    summary_file = evse_summary_file.replace(
        "charging_summary_",
        "charging_summary_stations_"
    )

    with open(
        summary_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "station_id",
                "plugs_used",
                "observations",
                "charging_minutes",
                "sessions"
            ]
        )

        writer.writeheader()
        writer.writerows(station_rows)

    return summary_file

def build_way_summary(station_summary_file):

    todos_file = "Todos.json"

    # ---------------------------------------------------------
    # Load station summary
    # ---------------------------------------------------------

    station_data = {}

    with open(
        station_summary_file,
        newline="",
        encoding="utf-8"
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:
            station_data[row["station_id"]] = {
                "plugs_used": int(row["plugs_used"]),
                "charging_minutes": int(row["charging_minutes"]),
                "sessions": int(row["sessions"])
            }

    # ---------------------------------------------------------
    # Build lookup using the station reference without
    # the 3-letter operator prefix.
    #
    # Example:
    # EDP-PTM-00069 -> PTM-00069
    # GAL-ABC-00123 -> ABC-00123
    # ---------------------------------------------------------

    station_lookup = {}

    for station_id in station_data:

        parts = station_id.split("-", 1)

        if len(parts) == 2:
            station_ref = parts[1]
            station_lookup[station_ref] = station_id

    # ---------------------------------------------------------
    # Read Todos.json
    # ---------------------------------------------------------

    with open(
        todos_file,
        "r",
        encoding="utf-8"
    ) as f:

        todos = json.load(f)

    # ---------------------------------------------------------
    # Build lookup of standalone charging stations from nodes.
    #
    # node:
    #     "ref": "LSB-90050"
    #     "capacity": "2"
    # ---------------------------------------------------------

    node_capacity = {}

    for element in todos.get("elements", []):

        if element.get("type") != "node":
            continue

        tags = element.get("tags", {})
        ref = tags.get("ref")

        if not ref:
            continue

        capacity = tags.get("capacity")

        if capacity is None:
            continue

        try:
            node_capacity[ref] = int(capacity)
        except (ValueError, TypeError):
            continue

    # ---------------------------------------------------------
    # Keep track of stations that have already
    # been assigned to a way.
    # ---------------------------------------------------------

    assigned_stations = set()

    way_rows = []

    # ---------------------------------------------------------
    # Process OSM ways
    # ---------------------------------------------------------

    for element in todos.get("elements", []):

        if element.get("type") != "way":
            continue

        tags = element.get("tags", {})
        ref = tags.get("ref")

        if not ref:
            continue

        refs = [
            r.strip()
            for r in ref.split(";")
            if r.strip()
        ]

        plugs_used = 0
        charging_minutes = 0
        sessions = 0
        stations = 0

        # -----------------------------------------------------
        # Match stations belonging to this way
        # -----------------------------------------------------

        for station_ref in refs:

            station_id = station_lookup.get(station_ref)

            if station_id is None:
                continue

            if station_id in assigned_stations:
                continue

            assigned_stations.add(station_id)

            stations += 1

            plugs_used += station_data[
                station_id
            ]["plugs_used"]

            charging_minutes += station_data[
                station_id
            ]["charging_minutes"]

            sessions += station_data[
                station_id
            ]["sessions"]

        # -----------------------------------------------------
        # Only include ways with charging activity
        # -----------------------------------------------------

        if stations > 0:

            # Use OSM way name when available,
            # otherwise use the OSM way ID.
            way_name = tags.get("name")

            if way_name:
                way_identifier = way_name
            else:
                way_identifier = element["id"]

            # -------------------------------------------------
            # Get physical capacity from OSM way.
            #
            # If unavailable or invalid, fall back to the
            # number of plugs actually used.
            # -------------------------------------------------

            capacity_value = tags.get("capacity")

            try:
                capacity = int(capacity_value)
            except (ValueError, TypeError):
                capacity = plugs_used

            # Avoid division by zero
            if capacity > 0:

                utilization = (
                    charging_minutes
                    / (capacity * 1440)
                    * 100
                )

            else:

                utilization = 0

            way_rows.append({
                "pool": way_identifier,
                "ref": ref,
                "stations": stations,
                "plugs_used": plugs_used,
                "capacity": capacity,
                "charging_minutes": charging_minutes,
                "sessions": sessions,
                "utilization": round(utilization, 2)
            })

    # ---------------------------------------------------------
    # Add stations that weren't associated with a way
    # ---------------------------------------------------------

    for station_id, values in station_data.items():

        if station_id in assigned_stations:
            continue

        # Remove the first three-letter prefix and hyphen.
        #
        # EDP-PTM-00069 -> PTM-00069
        # GAL-ABC-00123 -> ABC-00123
        parts = station_id.split("-", 1)

        if len(parts) == 2:
            station_ref = parts[1]
        else:
            station_ref = station_id

        plugs_used = values["plugs_used"]
        charging_minutes = values["charging_minutes"]

        # -----------------------------------------------------
        # Find physical capacity in the OSM node.
        #
        # If unavailable, fall back to plugs_used.
        # -----------------------------------------------------

        capacity = node_capacity.get(station_ref)

        if capacity is None or capacity <= 0:
            capacity = plugs_used

        # -----------------------------------------------------
        # Calculate utilization
        # -----------------------------------------------------

        if capacity > 0:

            utilization = (
                charging_minutes
                / (capacity * 1440)
                * 100
            )

        else:

            utilization = 0

        way_rows.append({
            "pool": station_ref,
            "ref": station_id,
            "stations": 1,
            "plugs_used": plugs_used,
            "capacity": capacity,
            "charging_minutes": charging_minutes,
            "sessions": values["sessions"],
            "utilization": round(utilization, 2)
        })

    # ---------------------------------------------------------
    # Sort by charging time, then sessions
    # ---------------------------------------------------------

    way_rows.sort(
        key=lambda r: (
            -r["charging_minutes"],
            -r["sessions"]
        )
    )

    # ---------------------------------------------------------
    # Write output
    # ---------------------------------------------------------

    summary_file = station_summary_file.replace(
        "charging_summary_stations_",
        "charging_summary_ways_"
    )

    with open(
        summary_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "pool",
                "ref",
                "stations",
                "plugs_used",
                "capacity",
                "charging_minutes",
                "sessions",
                "utilization"
            ]
        )

        writer.writeheader()
        writer.writerows(way_rows)

    return summary_file


def main():

    data = load_json()

    if not data:
        print("Input file is empty.")
        return

    raw_file = append_raw_observations(data)

    if raw_file:

        summary_file = build_summary(raw_file)

        station_summary_file = build_station_summary(
            summary_file
        )

        way_summary_file = build_way_summary(
            station_summary_file
        )

        print(f"Updated {raw_file}")
        print(f"Updated {summary_file}")
        print(f"Updated {station_summary_file}")
        print(f"Updated {way_summary_file}")


if __name__ == "__main__":
    main()
