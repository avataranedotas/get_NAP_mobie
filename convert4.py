from lookup_wiki import OPERATORS

from typing import List, Dict

from datetime import datetime

import json

import os

print("DEBUG: File size:", os.path.getsize("changes_add.json") if os.path.exists("changes_add.json") else "N/A")

try:
    with open("changes_add.json", "r", encoding="utf-8") as finput:
        stations: Dict[str, Dict] = json.load(finput)
except (FileNotFoundError, json.JSONDecodeError):
    stations = {}
    print("WARNING: changes_add.json missing or invalid — continuing with empty stations.")

def station_to_tags(station_id: str, data: Dict) -> List[str]:
    opc = data.get("opc")
    lookup_entry = OPERATORS.get(opc, {})

    tags: List[str] = []
    warnings: List[str] = []

    # Static tags
    tags += [
        f"LOCAL={data.get('latlon','24/7')}",
        "access=yes",
        "amenity=charging_station",
        "authentication:membership_card=yes",
        "authentication:none=no",
        "fee=yes",
        "maxstay=unlimited",
        "motorcar=yes",
        f"name={station_id}",
        f"ref={station_id}",
        "network=Mobi.E",
        "opening_hours=§§§§§",
        "parking:fee=§§§§§",
        "capacity=§§§§§",
    ]

    # Operator/brand from lookup
    if lookup_entry.get("brand"):
        tags.append(f"brand={lookup_entry['brand']}")
    if lookup_entry.get("brand:wikidata"):
        tags.append(f"brand:wikidata={lookup_entry['brand:wikidata']}")
    if lookup_entry.get("operator"):
        tags.append(f"operator={lookup_entry['operator']}")
    if lookup_entry.get("operator:wikidata"):
        tags.append(f"operator:wikidata={lookup_entry['operator:wikidata']}")
    if lookup_entry.get("email"):
        tags.append(f"email={lookup_entry['email']}")
    if lookup_entry.get("phone"):
        tags.append(f"phone={lookup_entry['phone']}")
    if lookup_entry.get("website"):
        tags.append(f"website={lookup_entry['website']}")
        
    # Payment (hardcoded for app and membership_card)
    payments = [p.lower() for p in data["stations"][0].get("payment", [])]
    tags += [
        "payment:app=yes",
        f"payment:cards={'yes' if any(x in p for p in payments for x in ('debit','credit')) else 'no'}",
        "payment:cash=no",
        "payment:membership_card=yes",
    ]

    # --- Connectors rework ---
    connector_mapping = {
        ("iec62196t2", "socket"): "socket:type2",
        ("iec62196t2", "cablemode3"): "socket:type2_cable",
        ("iec62196t2combo", "socket"): "socket:type2_combo",
        ("iec62196t2combo", "cablemode3"): "socket:type2_combo",
        ("chademo", "socket"): "socket:chademo",
        ("chademo", "cablemode3"): "socket:chademo",
    }

    evse_ids = []
    connector_summary: Dict[str, Dict[str, int]] = {}

    for evse in data["stations"][0].get("evses", []):
        evse_ident = evse["evse_id"]   # save it once
        #print (evse_ident)
        evse_ids.append(evse["evse_id"])
        for conn in evse.get("connectors", []):
            ctype = conn["connector_type"].lower()
            cformat = conn.get("connector_format", "").lower()
            cmode = conn.get("charging_mode", "").lower()
            #id_evse = conn.get("evse_id", "")
            tag = connector_mapping.get((ctype, cformat))
            #tag2 = connector_mapping.get((ctype, cformat, cmode))
            if not tag:
                continue

            current = int(float(conn.get("max_current", 0)))
            voltage = int(float(conn.get("voltage", 0)))
            power_w = float(conn.get("max_power", 0))
            power_kw = round(power_w / 1000, 1)

            # --- Warning conditions ---
            if tag in ("socket:type2", "socket:type2_cable"):
                
                if power_kw > 7.6 and voltage < 400:
                    #print (evse_ident)
                    warnings.append(
                        f"WARNING {station_id}/{evse_ident}: {tag} reports {power_kw}kW at {voltage}V (expected ~400V for >7.6kW)."
                    )
                if cmode=="mode2ac1p" and power_w > ((current * voltage) + 500):
                    #print ("mono_errado")
                    warnings.append(
                        f"WARNING {station_id}/{evse_ident}: {tag} power {power_w:.0f}W exceeds current*voltage ({current*voltage}W)."
                    )
                if cmode=="mode2ac1p" and power_w > 7600:
                    #print ("mono_demasiado")
                    warnings.append(
                        f"WARNING {station_id}/{evse_ident}: {tag} power {power_w:.0f}W singlephase power exceeds 7.6kW"
                    )
                if cmode=="mode3ac3p" and power_w > ((current * 240 * 3)+500):
                    #print ("tri_errado")
                    warnings.append(
                        f"WARNING {station_id}/{evse_ident}: {tag} power {power_w:.0f}W exceeds threephase current*voltage ({current*240*3}W)."
                    )


            if tag in ("socket:chademo", "socket:type2_combo"):
                if power_w > current * voltage:
                    warnings.append(
                        f"WARNING {station_id}/{evse_ident}: {tag} power {power_w:.0f}W exceeds current*voltage ({current*voltage}W)."
                    )

 

            # --- Aggregation ---
            if tag not in connector_summary:
                connector_summary[tag] = {
                    "count": 0,
                    "current": current,
                    "voltage": voltage,
                    "power": power_kw,
                }
            else:
                connector_summary[tag]["current"] = max(connector_summary[tag]["current"], current)
                connector_summary[tag]["voltage"] = max(connector_summary[tag]["voltage"], voltage)
                connector_summary[tag]["power"] = max(connector_summary[tag]["power"], power_kw)

            connector_summary[tag]["count"] += 1

    if evse_ids:
        tags.append(f"ref:EU:EVSE={';'.join(evse_ids)}")


    #for tag, values in connector_summary.items():
    #    tags.append(f"{tag}:current={values['current']}")
    #    if float(values["power"]).is_integer():
    #        potencia = f"{int(values['power'])}"
    #    else:
    #        potencia = f"{values['power']:.1f}"
    #   tags.append(f"{tag}:output={potencia} kW")
    #    tags.append(f"{tag}:voltage={values['voltage']}")
    #    tags.append(f"{tag}={values['count']}")


    for tag, values in connector_summary.items():
        # --- Special handling for CCS voltage ---
        if tag == "socket:type2_combo":
            voltage_val = 500 if values["voltage"] <= 500 else 1000
        else:
            voltage_val = values["voltage"]

        # Current stays unchanged
        tags.append(f"{tag}:current={values['current']}")

        # Power formatting
        if float(values["power"]).is_integer():
            potencia = str(int(values["power"]))
        else:
            potencia = f"{values['power']:.1f}"

        tags.append(f"{tag}:output={potencia} kW")
        tags.append(f"{tag}:voltage={voltage_val}")
        tags.append(f"{tag}={values['count']}")

    # return both tags and warnings
    return warnings + tags

# Write output for all stations
with open("stations_add_osm.txt", "a", encoding="utf-8") as f:
    # Write timestamp once at the top
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    f.write(f"# Generated on {timestamp}\n\n")
    for station_id, station_data in stations.items():
        f.write("\n".join(station_to_tags(station_id, station_data)))
        f.write("\n\n")  # blank line between stations
