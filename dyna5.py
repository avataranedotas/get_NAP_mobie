import json
from datetime import datetime
from typing import Set, List, Dict


def parse_latest_suspect_evses(txt_filepath: str) -> Set[str]:
    """Parse the latest timestamp block from the txt file and return all suspect EVSE codes."""
    suspect_evses = set()
    latest_block_lines = []
    current_block_lines = []
    current_timestamp = None

    with open(txt_filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if line.startswith("Timestamp:"):
                # Save previous block if exists
                if current_timestamp is not None:
                    latest_block_lines = current_block_lines
                current_block_lines = []
                current_timestamp = line

            elif "|" in line:
                evse_code = line.split("|")[0].strip()
                current_block_lines.append(evse_code)

    # Don't forget the last block — it's the latest
    if current_block_lines:
        latest_block_lines = current_block_lines

    suspect_evses = set(latest_block_lines)
    return suspect_evses


def find_fully_broken_stations(json_filepath: str, suspect_evses: Set[str]) -> List[Dict]:
    """Return stations where ALL their EVSE codes are in the suspect list."""
    with open(json_filepath, "r") as f:
        data = json.load(f)

    broken_stations = []

    for station_id, station_data in data.items():
        for station in station_data.get("stations", []):
            evses = station.get("evses", [])
            if not evses:
                continue

            all_evse_ids = [evse["evse_id"] for evse in evses]
            if all(evse_id in suspect_evses for evse_id in all_evse_ids):
                broken_stations.append({
                    "station_id": station_id,
                    "evse_ids": all_evse_ids,
                })

    return broken_stations


def append_to_output(output_filepath: str, broken_stations: List[Dict]):
    """Append flagged stations to the output file with a run timestamp."""
    run_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(output_filepath, "a") as f:
        f.write(f"Timestamp: {run_timestamp}\n")

        if not broken_stations:
            f.write("No fully disused stations found.\n")
        else:
            for station in broken_stations:
                evse_str = ";".join(station["evse_ids"])
                f.write(f"{station['station_id']} | {evse_str}\n")

        f.write("\n")

    print(f"[{run_timestamp}] Run complete. {len(broken_stations)} fully disused station(s) found.")
    for s in broken_stations:
        print(f"  {s['station_id']} | {';'.join(s['evse_ids'])}")


def main():
    txt_filepath = "disused_dyna_T2.txt"       # Path to your input txt file
    json_filepath = "LATEST_dynamic_mapped.json"           # Path to your JSON file
    output_filepath = "disused_dyna_T2_group.txt"

    suspect_evses = parse_latest_suspect_evses(txt_filepath)
    broken_stations = find_fully_broken_stations(json_filepath, suspect_evses)
    append_to_output(output_filepath, broken_stations)


if __name__ == "__main__":
    main()
