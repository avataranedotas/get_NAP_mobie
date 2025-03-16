import json
from collections import defaultdict


# Load JSON data from file
with open("LATEST_static.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Dictionary to store counts with (opc, opc_name) as key
opc_counts = defaultdict(int)

# Dictionary to store station prefix counts
prefix_counts = defaultdict(int)

# Loop through each entry and count occurrences
for station_id, entry in data.items():
    opc = entry.get("opc", "Unknown")
    opc_name = entry.get("opc_name", "Unknown")
    opc_counts[(opc, opc_name)] += 1  # Store counts by (opc, opc_name)
    # Extract the 3-letter prefix from the station ID and count
    prefix = station_id[:3]  # First 3 characters
    prefix_counts[prefix] += 1

# Sort results from most to least occurrences
sorted_opc_counts = sorted(opc_counts.items(), key=lambda x: x[1], reverse=True)
sorted_prefix_counts = sorted(prefix_counts.items(), key=lambda x: x[1], reverse=True)

# Write results to a file with opc, opc_name, and count
output_file = "opc_counts.csv"
with open(output_file, "w", encoding="utf-8") as file:
    for (opc, opc_name), count in sorted_opc_counts:
        file.write(f"{opc};{opc_name};{count}\n")
print(f"Results written to {output_file}")

# Write prefix counts to a separate file
prefix_output_file = "prefix_counts.csv"
with open(prefix_output_file, "w", encoding="utf-8") as file:
    for prefix, count in sorted_prefix_counts:
        file.write(f"{prefix};{count}\n")
print(f"Prefix counts written to {prefix_output_file}")

