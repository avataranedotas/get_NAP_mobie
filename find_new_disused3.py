
import json
from datetime import datetime, timedelta, timezone

# --- Configuration ---
stations_file = "LATEST_static.json"
updates_file = "charging_evses.json"

# --- Load JSON ---
with open(stations_file, "r", encoding="utf-8") as f:
    stations_data = json.load(f)

with open(updates_file, "r", encoding="utf-8") as f:
    updates_data = json.load(f)

# --- Build lookup of evse_id -> connector types ---
evse_connectors = {}
for site_id, site_data in stations_data.items():
    for station in site_data.get("stations", []):
        for evse in station.get("evses", []):
            evse_id = evse.get("evse_code")
            #print (evse_id)
            if not evse_id:
                continue
            connector_types = [
                conn.get("connector_type")
                for conn in evse.get("connectors", [])
                if "connector_type" in conn
            ]
            evse_connectors[evse_id] = connector_types

# --- Helper: safe ISO parser (works with 'Z') ---
def parse_iso_timestamp(ts):
    ts = ts.replace("Z", "+00:00")  # make timezone explicit
    try:
        return datetime.fromisoformat(ts)
    except Exception:
        # fallback parser
        return datetime.strptime(ts.split(".")[0], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)

# --- Step 1: find old timestamps ---
cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
old_evse_ids = []

for item in updates_data:
    try:
        last_updated = parse_iso_timestamp(item["lastUpdated"])
        if last_updated < cutoff_date:
            old_evse_ids.append(item["evse_id"])
    except Exception as e:
        print(f"Skipping {item}: {e}")

# --- Step 2: match EVSEs that have the iec62196T2COMBO connector ---
# ⚠ If your evse_id formats differ (like 'PT*GLG*EAVR*00031*02' vs 'AVR-00031-02'),
# you may need to extract the last part for matching.
def normalize_evse_id(eid):
    # Example: from "PT*GLG*EAVR*00031*02" → "AVR-00031-02"
    parts = eid.split("*")
    if len(parts) >= 4 and parts[-1].isdigit():
        return parts[-2] + "-" + parts[-1]
    return eid

# Build normalized lookup
normalized_lookup = {
    normalize_evse_id(eid): eid for eid in evse_connectors.keys()
}

old_combo_evse = []
for eid in old_evse_ids:
    norm = normalize_evse_id(eid)
    if norm in normalized_lookup:
        real_id = normalized_lookup[norm]
        if "iec62196T2COMBO" in evse_connectors[real_id]:
            old_combo_evse.append(real_id)

# --- Output ---
#print(f"\nFound {len(old_combo_evse)} EVSEs with outdated timestamps and T2COMBO connectors:")
now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
print(f"\n[{now_str}] Found {len(old_combo_evse)} EVSEs with outdated timestamps and T2COMBO connectors:")

for evse_id in old_combo_evse:
    print(evse_id)

with open("new_disused_3.txt", "w", encoding="utf-8") as f:
    json.dump(old_combo_evse, f, indent=2, ensure_ascii=False)





