import json
from datetime import datetime, timedelta
from collections import defaultdict

# Load the data 
with open('charging_evses.json', 'r') as file:
    data = json.load(file)

# Get the current time
current_time = datetime.utcnow()

# Define the cutoff time (X days ago)
cutoff_time = current_time - timedelta(days=45)

# Dictionary to group sub-IDs under the same main EVSE ID
evse_groups = defaultdict(list)

# Step 1: Organize data by main EVSE ID
for entry in data:
    try:
        last_updated_str = entry.get("lastUpdated")
        if last_updated_str:
            # Convert ISO 8601 timestamp to datetime
            last_updated = datetime.fromisoformat(last_updated_str.rstrip("Z"))

            # Extract the main EVSE identifier (before the last '-')
            evse_main_id = entry["evse_id"].rsplit('-', 1)[0]

            # Store timestamps under the main EVSE ID
            evse_groups[evse_main_id].append(last_updated)
    except Exception as e:
        print(f"Skipping invalid entry: {entry} | Error: {e}")

# Step 2: Identify "old" EVSE main IDs
old_evse_ids = set()

for evse_main_id, timestamps in evse_groups.items():
    # If all timestamps for this EVSE are older than 30 days, consider it "old"
    if all(timestamp < cutoff_time for timestamp in timestamps):
        old_evse_ids.add(evse_main_id)

# Step 3: Write the old EVSE-ids to a file
with open('old2.txt', 'w') as output_file:
    for evse_id in sorted(old_evse_ids):  # Sort for readability
        output_file.write(evse_id + "\n")

print(f"{len(old_evse_ids)} old entries written to old2.txt")

