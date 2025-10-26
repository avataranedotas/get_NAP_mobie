from datetime import datetime, timezone

# filter_evse_exact.py

input_evse_file = "new_disused_3.txt"   # File with EVSE IDs (output from previous script)
remove_file = "watchbusy.txt"          # File with lines to remove if fully matched
output_file = "new_disused_4.txt"        # Output file


# --- Load EVSE list (can be JSON-style or plain text) ---
with open(input_evse_file, "r", encoding="utf-8") as f:
    content = f.read().strip()

# Handle JSON-style list (starting with '[')
if content.startswith("["):
    import json
    evse_ids = json.loads(content)
else:
    evse_ids = [line.strip().strip('"').strip(",") for line in content.splitlines() if line.strip()]

# --- Load remove patterns ---
with open(remove_file, "r", encoding="utf-8") as f:
    remove_patterns = [line.strip() for line in f if line.strip()]

# --- Filtering ---
filtered = []
for evse in evse_ids:
    if not any(pattern in evse for pattern in remove_patterns):
        filtered.append(evse)


# --- Write output ---
timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

with open(output_file, "a", encoding="utf-8") as f:
    f.write(f"{timestamp}\n")
    for evse in filtered:
        f.write(f"{evse}\n")
    f.write("\n\n")

print(f"Filtered {len(evse_ids) - len(filtered)} EVSEs; {len(filtered)} kept.")
print(f"Output written to: {output_file}")
