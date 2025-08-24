from lookup_wiki import OPERATORS

from typing import List, Dict

import json

# Load the input stations file (JSON)
with open("changes_add.json", "r", encoding="utf-8") as finput:
    stations: Dict[str, Dict] = json.load(finput)

def station_to_tags(station_id: str, data: Dict) -> List[str]:
    opc = data.get("opc")
    lookup_entry = OPERATORS.get(opc, {})

    tags: List[str] = []
    warnings: List[str] = []

    # Static tags
    tags += [
        f"LOCAL={data.get('latlon','24/7')}",
        "access=yes",
        "construction:amenity=charging_station",
        "authentication:membership_card=yes",
        "authentication:none=no",
        "authentication:app=yes",
        "fee=yes",
        "maxstay=unlimited",
        "motorcar=yes",
        f"name={station_id}",
        "network=Mobi.E",
        "opening_hours=§§§§§",
        "parking:fee=§§§§§",
        "website=https://www.mobie.pt",
        f"ref={station_id}",
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
        evse_ids.append(evse["evse_id"])
        for conn in evse.get("connectors", []):
            ctype = conn["connector_type"].lower()
            cformat = conn.get("connector_format", "").lower()
            tag = connector_mapping.get((ctype, cformat))
            if not tag:
                continue

            current = int(float(conn.get("max_current", 0)))
            voltage = int(float(conn.get("voltage", 0)))
            power_w = float(conn.get("max_power", 0))
            power_kw = int(round(power_w / 1000))

            # --- Warning conditions ---
            if tag in ("socket:type2", "socket:type2_cable"):
                if power_kw > 7.6 and voltage < 400:
                    warnings.append(
                        f"WARNING {station_id}: {tag} reports {power_kw}kW at {voltage}V (expected ~400V for >7.6kW)."
                    )

            if tag in ("socket:chademo", "socket:type2_combo"):
                if power_w > current * voltage:
                    warnings.append(
                        f"WARNING {station_id}: {tag} power {power_w:.0f}W exceeds current*voltage ({current*voltage}W)."
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

    for tag, values in connector_summary.items():
        tags.append(f"{tag}:current={values['current']}")
        tags.append(f"{tag}:output={values['power']} kW")
        tags.append(f"{tag}:voltage={values['voltage']}")
        tags.append(f"{tag}={values['count']}")

    # return both tags and warnings
    return warnings + tags

# Write output for all stations
with open("stations_add_osm.txt", "a", encoding="utf-8") as f:
    for station_id, station_data in stations.items():
        f.write("\n".join(station_to_tags(station_id, station_data)))
        f.write("\n\n")  # blank line between stations

