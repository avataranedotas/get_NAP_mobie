import json
from datetime import datetime, timezone, timedelta


def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_exclusion_list(filepath):
    """Load a plain text list, one evse_id per line. Returns empty set if file not found."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        print("Warning: {} not found, skipping exclusion.".format(filepath))
        return set()


def build_evse_connector_map(static_data):
    """Build a lookup map: evse_id -> list of connector_types for that evse."""
    mapping = {}
    for station_data in static_data.values():
        for station in station_data.get("stations", []):
            for evse in station.get("evses", []):
                evse_id = evse.get("evse_id")
                connector_types = [
                    c.get("connector_type")
                    for c in evse.get("connectors", [])
                ]
                if evse_id:
                    mapping[evse_id] = connector_types
    return mapping


def check_disused(tracker_path, static_path, output_path, watchlist_path, ignore_path, days=30):
    tracker = load_json(tracker_path)
    static_data = load_json(static_path)

    connector_map = build_evse_connector_map(static_data)
    watchlist = load_exclusion_list(watchlist_path)
    ignore_list = load_exclusion_list(ignore_path)

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)

    disused = []

    for evse_id, info in tracker.items():
        last_seen = info.get("last_seen_charging")

        # Skip null values
        if last_seen is None:
            continue

        # Parse timestamp
        try:
            last_seen_dt = datetime.strptime(last_seen, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        except ValueError:
            print("Warning: could not parse timestamp for {} - skipping.".format(evse_id))
            continue

        # Check if older than 30 days
        if last_seen_dt < cutoff:
            connector_types = connector_map.get(evse_id, [])
            if "iec62196T2COMBO" in connector_types:
                # Skip if in watchlist or ignore list
                if evse_id in watchlist:
                    print("Skipping {} (found in watchbusy_dyna.txt)".format(evse_id))
                    continue
                if evse_id in ignore_list:
                    print("Skipping {} (found in ignore_dyna.txt)".format(evse_id))
                    continue
                disused.append({
                    "evse_id": evse_id,
                    "station_id": info.get("station_id")
                })

    if not disused:
        print("No disused CCS EVSEs found older than {} days. Nothing written.".format(days))
        return

    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    with open(output_path, "a", encoding="utf-8") as f:
        f.write("Timestamp: {}\n".format(timestamp))
        for entry in sorted(disused, key=lambda x: x["evse_id"]):
            f.write("{} | station: {}\n".format(
                entry["evse_id"],
                entry["station_id"]
            ))
        f.write("\n")

    print("Timestamp: {}".format(timestamp))
    print("{} disused CCS EVSE(s) found (not charged in {} days):".format(len(disused), days))
    for entry in sorted(disused, key=lambda x: x["evse_id"]):
        print("  {} | station: {}".format(
            entry["evse_id"],
            entry["station_id"]
        ))


if __name__ == "__main__":
    check_disused(
        tracker_path="charging_tracker_dedup.json",
        static_path="LATEST_static.json",
        output_path="disused_dyna_CCS.txt",
        watchlist_path="watchbusy_dyna.txt",
        ignore_path="ignore_dyna.txt"
    )
