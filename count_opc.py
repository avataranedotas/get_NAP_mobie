import json
import csv
from collections import defaultdict

# Load JSON
with open("LATEST_static.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Aggregate by OPC code
opc_counts = defaultdict(int)
opc_names = defaultdict(set)

for entry in data.values():
    opc = entry.get("opc", "Unknown")
    opc_name = entry.get("opc_name", "Unknown")
    opc_counts[opc] += 1
    opc_names[opc].add(opc_name)

# Aggregate by prefix
prefix_counts = defaultdict(int)
for station_id in data.keys():
    prefix = station_id[:3] if len(station_id) >= 3 else station_id
    prefix_counts[prefix] += 1

# Sort results
sorted_opc_counts = sorted(opc_counts.items(), key=lambda x: x[1], reverse=True)
sorted_prefix_counts = sorted(prefix_counts.items(), key=lambda x: x[1], reverse=True)

# Helper to write CSV/TSV
def write_counts(filename, header, rows, delimiter=";"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerow(header)
        writer.writerows(rows)

# Write OPC counts with joined names
opc_rows = [(opc, ", ".join(sorted(opc_names[opc])), count) for opc, count in sorted_opc_counts]
write_counts("opc_counts.csv", ["OPC", "Names", "Count"], opc_rows, ";")
write_counts("opc_counts.tsv", ["OPC", "Names", "Count"], opc_rows, "\t")

# Write prefix counts
write_counts("prefix_counts.csv", ["Prefix", "Count"], sorted_prefix_counts, ";")
write_counts("prefix_counts.tsv", ["Prefix", "Count"], sorted_prefix_counts, "\t")

print("All results written successfully.")
