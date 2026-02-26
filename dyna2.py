import json


def load_json(filepath: str) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, filepath: str) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Saved: {filepath}")


def extract_charging(input_path: str, output_path: str) -> None:
    data = load_json(input_path)

    charging_evses = []

    for station_id, station_data in data.items():
        for station in station_data.get("stations", []):
            for evse in station.get("evses", []):
                if evse.get("evse_status") == "charging":
                    charging_evses.append({
                        "station_id": station_id,
                        "evse_id": evse.get("evse_id"),
                        "lastUpdated": station_data.get("lastUpdated")
                    })

    save_json(charging_evses, output_path)
    print(f"Found {len(charging_evses)} charging EVSE(s).")


if __name__ == "__main__":
    extract_charging(
        input_path="LATEST_dynamic_mapped.json",
        output_path="charging_evses_dyna.json"
    )
