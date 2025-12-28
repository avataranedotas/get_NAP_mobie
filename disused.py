import json
from datetime import datetime, timedelta

def load_dict_from_json(file_path):
    with open(file_path, 'r', encoding="utf-8") as file:
        return json.load(file)

def parse_iso8601(ts):
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(ts, fmt)
        except ValueError:
            pass
    raise ValueError(f"Unsupported date format: {ts}")

latest = load_dict_from_json("LATEST_static.json")

current_date = datetime.utcnow()

cutoff_30 = current_date - timedelta(days=30)
cutoff_60 = current_date - timedelta(days=60)

old = []        # T2COMBO, >30 days
old_ac = []     # all stations, >60 days

for station_id, station_data in latest.items():

    last_updated_str = station_data.get("lastUpdated")
    if not last_updated_str:
        continue

    try:
        last_updated = parse_iso8601(last_updated_str)
    except ValueError:
        continue

    # ---------- old_ac.txt logic (no connector filtering) ----------
    if last_updated < cutoff_60:
        old_ac.append(station_id)

    # ---------- old.txt logic (T2COMBO + 30 days) ----------
    if last_updated >= cutoff_30:
        continue

    has_t2combo = False
    for station in station_data.get("stations", []):
        for evse in station.get("evses", []):
            for connector in evse.get("connectors", []):
                if connector.get("connector_type") == "iec62196T2COMBO":
                    has_t2combo = True
                    break
            if has_t2combo:
                break
        if has_t2combo:
            break

    if has_t2combo:
        old.append(station_id)

# ---------- Write outputs ----------
if old:
    with open("old.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(old))

if old_ac:
    with open("old_ac.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(old_ac))
