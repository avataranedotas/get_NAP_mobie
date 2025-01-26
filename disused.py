import json
from datetime import datetime, timedelta


# Load dictionaries from JSON files
def load_dict_from_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# File paths
file1 = "LATEST_static.json"

latest = load_dict_from_json(file1)

# Get the current date and time
current_date = datetime.utcnow()

# Calculate the date 30 days ago from today
thirty_days_ago = current_date - timedelta(days=30)

# storage of old updated
old = []

# Loop through the dictionary to check if 'lastUpdated' is older than 1 month
for station_id, station_data in latest.items():
    last_updated_str = station_data["lastUpdated"]
    # Parse the lastUpdated string into a datetime object
    last_updated = datetime.strptime(last_updated_str, "%Y-%m-%dT%H:%M:%S.%fZ")

    # Compare if the lastUpdated timestamp is older than 1 month
    if last_updated < thirty_days_ago:
        old.append(station_id)
        #print(f"{station_id}")

#print (old)

if old:
    # Write to file
    with open("old.txt", "w") as output_file:
        output_file.writelines(f"{line}\n" for line in old)

