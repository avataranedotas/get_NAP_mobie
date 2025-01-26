import json
from deepdiff import DeepDiff
from datetime import datetime


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


diff = DeepDiff(
    latest,
    previous,
    exclude_regex_paths=[r".*['\"]lastUpdated['\"].*"]
)

print (diff)

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if diff:
    
    try:
        json_data = json.dumps(diff, indent=4)
        with open(f"changes.txt", "a") as file:
            file.write (str(timestamp))
            file.write ("\n")
            json.dump(diff, file, indent=4)
            
    except TypeError as e:
        print(f"Serialization error: {e}")
        
