import json


def load_json(filepath: str) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: dict, filepath: str) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Saved: {filepath}")


def build_evse_code_to_id_map(static_data):
    mapping = {}

    for station_data in static_data.values():
        for station in station_data.get("stations", []):
            station_id = station.get("station_id")

            for evse in station.get("evses", []):
                evse_code = evse.get("evse_code")
                evse_id = evse.get("evse_id")

                if station_id and evse_code and evse_id:
                    mapping[(station_id, evse_code)] = evse_id

    return mapping


def merge(static_path: str, dynamic_path: str, output_path: str) -> None:
    static_data = load_json(static_path)
    dynamic_data = load_json(dynamic_path)

    # Build lookup: evse_code -> evse_id
    evse_map = build_evse_code_to_id_map(static_data)

    unmatched = []
    output_data = {}

    for station_id, station_dynamic in dynamic_data.items():
        new_station = {
            "lastUpdated": station_dynamic.get("lastUpdated"),
            "stations": []
        }

        for station in station_dynamic.get("stations", []):
            new_evses = []
            for evse in station.get("evses", []):
                station_id = station.get("station_id")
                evse_code = evse.get("evse_id")

                proper_evse_id = evse_map.get((station_id, evse_code))

                if proper_evse_id:
                    new_evses.append({
                        "evse_id": proper_evse_id,
                        "evse_status": evse.get("evse_status")
                    })
                else:
                    unmatched.append(evse_code)
                    # Keep original if no match found
                    new_evses.append(evse)

            new_station["stations"].append({
                "station_id": station.get("station_id"),
                "evses": new_evses
            })

        output_data[station_id] = new_station

    save_json(output_data, output_path)

    if unmatched:
        print(f"\nWarning: {len(unmatched)} evse_code(s) had no match in static data:")
        for code in unmatched:
            print(f"  - {code}")
    else:
        print("All evse codes successfully mapped to evse_ids.")


if __name__ == "__main__":
    merge(
        static_path="LATEST_static.json",
        dynamic_path="LATEST_dynamic.json",
        output_path="LATEST_dynamic_mapped.json"
    )
