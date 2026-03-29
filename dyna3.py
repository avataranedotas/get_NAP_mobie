import json
from datetime import datetime, timezone
from typing import Union


def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("Saved: {}".format(filepath))


def load_tracker(filepath):
    """Load existing tracker, or return empty dict if file doesn't exist."""
    try:
        return load_json(filepath)
    except FileNotFoundError:
        return {}


def update_charging_tracker(input_path, tracker_path):
    data = load_json(input_path)
    tracker = load_tracker(tracker_path)

    run_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    updated_count = 0
    new_count = 0

    for station_id, station_data in data.items():
        for station in station_data.get("stations", []):
            for evse in station.get("evses", []):
                evse_id = evse.get("evse_id")
                status = evse.get("evse_status")

                if evse_id not in tracker:
                    tracker[evse_id] = {
                        "station_id": station_id,
                        "last_seen_charging": run_timestamp if status == "charging" else None
                    }
                    new_count += 1
                elif status == "charging":
                    tracker[evse_id]["last_seen_charging"] = run_timestamp
                    updated_count += 1

    save_json(tracker, tracker_path)
    print("Run at: {}".format(run_timestamp))
    print("New evse_ids added: {}".format(new_count))
    print("Charging timestamps updated: {}".format(updated_count))
    print("Total evse_ids tracked: {}".format(len(tracker)))


if __name__ == "__main__":
    update_charging_tracker(
        input_path="LATEST_dynamic_mapped.json",
        tracker_path="charging_tracker.json"
    )
