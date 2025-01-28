import json
from datetime import datetime

# Function to remove the `lastUpdated` field recursively
def remove_timestamps(data):
    if isinstance(data, dict):
        # Remove 'lastUpdated' key if it exists
        data = {k: remove_timestamps(v) for k, v in data.items() if k != "lastUpdated"}
    elif isinstance(data, list):
        # Apply to each item in a list
        data = [remove_timestamps(item) for item in data]
    return data


# Function to recursively find differences
def find_differences(old, new):
    differences = {}
    if isinstance(old, dict) and isinstance(new, dict):
        for key in old.keys() | new.keys():
            if key in old and key in new:
                diff = find_differences(old[key], new[key])
                if diff:  # Add only if there are differences
                    differences[key] = diff
            elif key in old:
                differences[key] = {"removed": old[key]}
            elif key in new:
                differences[key] = {"added": new[key]}
    elif isinstance(old, list) and isinstance(new, list):
        # Compare lists element by element (assuming same order)
        for i, (o_item, n_item) in enumerate(zip(old, new)):
            diff = find_differences(o_item, n_item)
            if diff:
                differences[i] = diff
        # Handle extra elements in new or old list
        if len(old) > len(new):
            differences["removed_items"] = old[len(new) :]
        if len(new) > len(old):
            differences["added_items"] = new[len(old) :]
    else:
        if old != new:
            differences = {"old": old, "new": new}
    return differences

# Load dictionaries from JSON files
def load_dict_from_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# File paths
file1 = "LATEST_static.json"
file2 = "PREVIOUS_static.json"

# Load dictionaries
latest = load_dict_from_json(file1)
previous = load_dict_from_json(file2)

# Remove timestamps from both dictionaries
latest_no_timestamps = remove_timestamps(latest)
previous_no_timestamps = remove_timestamps(previous)

adicionados = {}
removidos = {}
modificados ={}

adicionados = {key: value for key, value in latest.items() if key not in previous}

removidos = [
    key for key in previous_no_timestamps if key not in latest_no_timestamps
]


# Find modified fields (only differences)
modificados = {
    key: find_differences(previous_no_timestamps[key], latest_no_timestamps[key])
    for key in latest_no_timestamps
    if key in previous_no_timestamps and previous_no_timestamps[key] != latest_no_timestamps[key]
}

if adicionados:
    print("Adicionados:")    
    print(json.dumps(adicionados, indent=4, ensure_ascii=False))

if removidos:
    print("Removidos:")    
    print(json.dumps(removidos, indent=4, ensure_ascii=False))

if modificados:
    print("Modificados:")
    print(json.dumps(modificados, indent=4, ensure_ascii=False))


timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

with open("changes.txt", "a", encoding="utf-8") as file:
    if adicionados or removidos or modificados :
        file.write (str(timestamp))
        file.write ("\n")

    if adicionados :
        file.write ("Adicionados:\n")
        json.dump(adicionados, file, indent=4, ensure_ascii=False)
        file.write ("\n")

    if removidos :
        file.write ("Removidos:\n")
        json.dump(removidos, file, indent=4, ensure_ascii=False)
        file.write ("\n")

    if modificados:
        file.write("Modificados:\n")
        json.dump(modificados, file, indent=4, ensure_ascii=False)
        file.write("\n")


