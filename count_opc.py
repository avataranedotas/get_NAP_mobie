import json
from collections import defaultdict

# Load JSON data from file
with open("LATEST_static.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Dictionary to store counts with (opc, opc_name) as key
opc_counts = defaultdict(int)

# Loop through each entry and count occurrences
for entry in data.values():
    opc = entry.get("opc", "Unknown")
    opc_name = entry.get("opc_name", "Unknown")
    opc_counts[(opc, opc_name)] += 1  # Store counts by (opc, opc_name)

# Sort results from most to least occurrences
sorted_opc_counts = sorted(opc_counts.items(), key=lambda x: x[1], reverse=True)

# Write results to a file with opc, opc_name, and count
output_file = "opc_counts.csv"
with open(output_file, "w", encoding="utf-8") as file:
    for (opc, opc_name), count in sorted_opc_counts:
        file.write(f"{opc};{opc_name};{count}\n")

print(f"Results written to {output_file}")
