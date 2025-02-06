import json
from collections import defaultdict

# Load JSON data from file
with open("LATEST_static.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Dictionary to store counts
opc_counts = defaultdict(int)

# Loop through each entry and count based on opc_name
for entry in data.values():
    opc_name = entry.get("opc", "Unknown")
    opc_counts[opc_name] += 1

# Sort results from most to least occurrences
sorted_opc_counts = sorted(opc_counts.items(), key=lambda x: x[1], reverse=True)

# Print results
#for opc, count in sorted_opc_counts:
#    print(f"{opc};{count}")

# Write results to a file
output_file = "opc_counts.txt"

with open(output_file, "w", encoding="utf-8") as file:
    for opc, count in sorted_opc_counts:
        file.write(f"{opc};{count}\n")

print(f"Results written to {output_file}")
