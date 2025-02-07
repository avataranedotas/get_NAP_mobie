import json

# Load previous results if available
def load_previous_results(filename):
    try:
        with open(filename, "r") as infile:
            return json.load(infile)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Load latest dynamic data
def load_latest_data(filename):
    try:
        with open(filename, "r") as infile:
            return json.load(infile)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Save updated results
def save_results(filename, data):
    with open(filename, "w") as outfile:
        json.dump(data, outfile, indent=4)

# Load data from file
json_data = load_latest_data("LATEST_dynamic.json")

# Load previous results
filename = "charging_evses.json"
previous_results = load_previous_results(filename)

# Extract EVSEs with "charging" status
charging_evses = {evse["evse_id"]: evse for evse in previous_results}  # Use dictionary to avoid duplicates

for station_key, station_data in json_data.items():
    timestamp = station_data["lastUpdated"]
    for station in station_data["stations"]:
        for evse in station["evses"]:
            if evse["evse_status"] == "charging":
                charging_evses[evse["evse_id"]] = {"evse_id": evse["evse_id"], "lastUpdated": timestamp}

# Convert back to list and save
save_results(filename, list(charging_evses.values()))

print("Charging EVSEs data updated and saved to charging_evses.json")

