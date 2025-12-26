import json
from datetime import datetime, timedelta


# Load dictionaries from JSON files
def load_dict_from_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# File paths
file1 = "LATEST_static.json"


def parse_iso8601(ts):
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(ts, fmt)
        except ValueError:
            pass
    raise ValueError(f"Unsupported date format: {ts}")


latest = load_dict_from_json(file1)

# Get the current date and time
current_date = datetime.utcnow()

# Calculate the date 30 days ago from today
thirty_days_ago = current_date - timedelta(days=30)
cutoff_date = current_date - timedelta(days=30)

# storage of old updated
old = []

# Loop through the dictionary to check if 'lastUpdated' is older than 1 month
for station_id, station_data in latest.items():

    # --- Check lastUpdated ---
    last_updated_str = station_data.get("lastUpdated")
    if not last_updated_str:
        continue

    try:
        last_updated = parse_iso8601(last_updated_str)
    except ValueError:
        continue

    if last_updated >= cutoff_date:
        continue

    # --- Check for at least one iec62196T2COMBO connector ---
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

#print (old)

if old:
    # Write to file
    with open("old.txt", "w") as output_file:
        output_file.writelines(f"{line}\n" for line in old)

