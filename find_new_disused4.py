# filter_evse_exact.py

input_evse_file = "new_disused_3.txt"   # File with EVSE IDs (output from previous script)
remove_file = "watchbusy.txt"          # File with lines to remove if fully matched
output_file = "new_disused_4.txt"        # Output file

# --- Load EVSE IDs ---
with open(input_evse_file, "r", encoding="utf-8") as f:
    evse_ids = [line.strip() for line in f if line.strip()]

# --- Load Remove List ---
with open(remove_file, "r", encoding="utf-8") as f:
    remove_patterns = [line.strip() for line in f if line.strip()]

# --- Filtering ---
filtered = []
for evse in evse_ids:
    # Keep the EVSE unless one of the remove patterns matches exactly as a substring
    # (we check for "-pattern" or "*pattern*" boundaries to avoid accidental partial matches)
    should_remove = False
    for pattern in remove_patterns:
        # Only remove if the whole pattern is present as a complete segment
        if pattern in evse:
            should_remove = True
            break
    if not should_remove:
        filtered.append(evse)

# --- Output Results ---
with open(output_file, "w", encoding="utf-8") as f:
    for evse in filtered:
        f.write(evse + "\n")

print(f"Filtered {len(evse_ids) - len(filtered)} EVSEs; {len(filtered)} kept.")
print(f"Output written to: {output_file}")

