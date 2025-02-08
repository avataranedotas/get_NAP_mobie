import json
from datetime import datetime, timedelta

# Load the data 
with open('charging_evses.json', 'r') as file:
    data = json.load(file)

# Get the current time
current_time = datetime.utcnow()

# Define the cutoff time (5 days ago)
cutoff_time = current_time - timedelta(hours=5)

# Filter out entries older than 5 days
old_entries = [entry["evse_id"].rsplit('-', 1)[0] for entry in data if datetime.fromisoformat(entry["lastUpdated"].replace("Z", "")) < cutoff_time]

# Write the filtered EVSE-ids to a new file
with open('old2.txt', 'w') as output_file:
    for evse_id in old_entries:
        output_file.write(evse_id + "\n")

print(f"{len(old_entries)} old entries written to old2.txt")


