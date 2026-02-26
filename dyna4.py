import json
from datetime import datetime


def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_watchlist(filepath):
    """Load watched evse_ids from plain text file, one per line."""
    with open(filepath, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())


def check_and_log(charging_path, watchlist_path, output_path):
    charging_data = load_json(charging_path)
    watchlist = load_watchlist(watchlist_path)

    # Build a set of evse_ids currently charging
    charging_ids = set(entry.get("evse_id") for entry in charging_data)

    # Find watched evses that are currently charging
    matches = watchlist.intersection(charging_ids)

    if not matches:
        print("No watched EVSEs currently charging. Nothing written.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(output_path, "a", encoding="utf-8") as f:
        f.write("Timestamp: {}\n".format(timestamp))
        for evse_id in sorted(matches):
            f.write("{}\n".format(evse_id))

    print("Timestamp: {}".format(timestamp))
    print("{} watched EVSE(s) found charging:".format(len(matches)))
    for evse_id in sorted(matches):
        print("  {}".format(evse_id))


if __name__ == "__main__":
    check_and_log(
        charging_path="charging_evses_dyna.json",
        watchlist_path="watchbusy_dyna.txt",
        output_path="charging_dyna.txt"
    )
