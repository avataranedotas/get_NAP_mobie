import json

with open('charging_tracker.json', 'r') as f:
    data = json.load(f)

filtered = {k: v for k, v in data.items() if k.startswith('PT*')}

with open('charging_tracker_filtered.json', 'w') as f:
    json.dump(filtered, f, indent=4)

print(f"Removed {len(data) - len(filtered)} entries. {len(filtered)} remaining.")
