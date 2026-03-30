import json
from datetime import datetime

with open('charging_tracker.json', 'r') as f:
    data = json.load(f)

PREFIXES = ('PT*EDP', 'PT*GLP', 'PT*MLT')

def get_connector_number(key):
    last = key.split('*')[-1]
    return str(int(last))

def parse_date(val):
    if val is None:
        return datetime.min
    # Remove the Z and parse manually
    val = val.replace('Z', '').split('.')[0]  # "2026-03-29T16:30:24"
    return datetime.strptime(val, '%Y-%m-%dT%H:%M:%S')

# ── EDP / GLP / MLT: same logic as before ─────────────────────────────────────
prefix_groups = {}
for key, val in data.items():
    if not key.startswith(PREFIXES):
        continue
    station = val['station_id']
    try:
        connector = get_connector_number(key)
    except ValueError:
        continue
    prefix_groups.setdefault((station, connector), []).append(key)

to_delete = set()
for group_key, keys in prefix_groups.items():
    if len(keys) > 1:
        keys_sorted = sorted(keys, key=lambda k: len(k))
        to_delete.update(keys_sorted[1:])
        print(f"Keeping '{keys_sorted[0]}', deleting {keys_sorted[1:]}")

# ── Other prefixes: group by stripped key, keep most recent ───────────────────
other_groups = {}
for key, val in data.items():
    if key.startswith(PREFIXES):
        continue
    stripped = key.replace('*', '')
    other_groups.setdefault(stripped, []).append(key)

warnings = []
for stripped, keys in other_groups.items():
    if len(keys) > 1:
        keys_sorted = sorted(keys, key=lambda k: parse_date(data[k]['last_seen_charging']), reverse=True)
        kept = keys_sorted[0]
        deleted = keys_sorted[1:]
        to_delete.update(deleted)
        warnings.append(
            f"station {data[kept]['station_id']} stripped key '{stripped}':\n"
            f"  keeping:  '{kept}' (last_seen: {data[kept]['last_seen_charging']})\n"
            f"  deleting: {[(k, data[k]['last_seen_charging']) for k in deleted]}\n"
        )

# ── Apply deletions ────────────────────────────────────────────────────────────
for key in to_delete:
    del data[key]

with open('charging_tracker_dedup.json', 'w') as f:
    json.dump(data, f, indent=4)

if warnings:
    with open('warnings_tracker.txt', 'a') as f:
        f.write(f"\n--- Run {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        for w in warnings:
            f.write(f"WARNING: duplicate non-allowed keys for {w}")
    print(f"{len(warnings)} warning(s) written to warnings_tracker.txt")

print(f"Removed {len(to_delete)} duplicate entries. {len(data)} remaining.")

